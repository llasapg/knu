import os
import shutil
import json
import time
import hmac
import hashlib
import base64
import requests
import urllib.parse
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from azure.storage.blob import BlobServiceClient
from azure.eventhub import EventHubConsumerClient

IOTHUB_CONNECTION_STR = ""
IOTHUB_SERVICE_STR = ""
BLOB_CONN_STR = ""

EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")
DEVICE_ID = os.getenv("DEVICE_ID", "test_1")

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class AnomalyTrainer:
    def __init__(self, sequence_length=10, features=3):
        self.buffer = []
        self.is_calibrating = False
        self.seq_len = sequence_length
        self.features = features
        self.temp_model_path = "temp_smartiot_export"
        self.min_vals = None
        self.max_vals = None

    def generate_sas_token(self, host, key, policy_name, expiry=3600):
        import urllib.parse
        import time
        import hmac
        import hashlib
        import base64

        ttl = int(time.time()) + expiry
        uri = host.lower().strip()
        encoded_uri = urllib.parse.quote(uri, safe='')
        string_to_sign = f"{encoded_uri}\n{ttl}"

        decoded_key = base64.b64decode(key)
        signature = hmac.new(decoded_key, string_to_sign.encode('utf-8'), hashlib.sha256).digest()
        encoded_sig = base64.b64encode(signature).decode('utf-8')
        url_encoded_sig = urllib.parse.quote(encoded_sig, safe='')

        return f"SharedAccessSignature sr={encoded_uri}&sig={url_encoded_sig}&se={ttl}&skn={policy_name}"

    def update_device_twin(self, threshold, blob_url):
        try:
            # Парсим строку подключения
            parts = dict(item.split('=', 1) for item in IOTHUB_SERVICE_STR.split(';'))
            host = parts['HostName'].strip()
            key_name = parts['SharedAccessKeyName'].strip()
            key_val = parts['SharedAccessKey'].strip()

            # Генерируем токен (используем только HostName, как в рабочем коде)
            token = self.generate_sas_token(host, key_val, key_name)

            dev_id = DEVICE_ID.strip()
            # Используем актуальную версию API
            url = f"https://{host}/twins/{dev_id}?api-version=2020-03-13"

            headers = {
                'Authorization': token,
                'Content-Type': 'application/json'
            }

            # Подготавливаем патч с учетом нормализации
            patch = {
                "properties": {
                    "desired": {
                        "model_threshold": float(threshold),
                        "model_url": blob_url,
                        "min_vals": self.min_vals.tolist() if self.min_vals is not None else [],
                        "max_vals": self.max_vals.tolist() if self.max_vals is not None else []
                    }
                }
            }

            print(f"[*] Sending update to Twin: {url}")
            response = requests.patch(url, json=patch, headers=headers)

            if response.status_code in [200, 204]:
                print(f"[SUCCESS] Device Twin updated for {dev_id}")
            else:
                print(f"[ERROR] Twin update failed: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"[ERROR] REST update failed: {e}")

    def bytes_to_c_array(self, data, threshold, var_name="smartiot_model"):
        hex_data = [f"0x{b:02x}" for b in data]
        c_code = f"#ifndef MODEL_DATA_H\n#define MODEL_DATA_H\n\nunsigned char {var_name}[] = {{\n  "
        c_code += ", ".join(hex_data)
        c_code += f"\n}};\n\nunsigned int {var_name}_len = {len(data)};\n"
        c_code += f"float {var_name}_threshold = {threshold:.6f};\n\n#endif"
        return c_code

    def train_and_upload(self):
        if len(self.buffer) < self.seq_len + 50:
            print(f"[!] Not enough data: {len(self.buffer)}")
            return

        raw_data = np.array(self.buffer)
        self.min_vals = raw_data.min(axis=0)
        self.max_vals = raw_data.max(axis=0)
        norm_data = (raw_data - self.min_vals) / (self.max_vals - self.min_vals + 1e-7)

        sequences = []
        for i in range(len(norm_data) - self.seq_len):
            sequences.append(norm_data[i : i + self.seq_len].flatten())

        train_x = np.array(sequences)
        input_dim = self.seq_len * self.features

        model = models.Sequential([
            layers.Input(shape=(input_dim,)),
            layers.Dense(8, activation='relu'),
            layers.Dense(4, activation='relu'),
            layers.Dense(8, activation='relu'),
            layers.Dense(input_dim, activation='linear')
        ])

        model.compile(optimizer='adam', loss='mse')
        model.fit(train_x, train_x, epochs=60, batch_size=16, validation_split=0.1, verbose=1)

        reconstructions = model.predict(train_x)
        mse = np.mean(np.square(train_x - reconstructions), axis=1)
        threshold = np.percentile(mse, 98)

        if os.path.exists(self.temp_model_path):
            shutil.rmtree(self.temp_model_path)
        model.export(self.temp_model_path)

        try:
            converter = tf.lite.TFLiteConverter.from_saved_model(self.temp_model_path)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            tflite_model_bytes = converter.convert()

            h_file_content = self.bytes_to_c_array(tflite_model_bytes, threshold)
            blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
            blob_client = blob_service_client.get_blob_client(container="models", blob=f"{DEVICE_ID}/model_data.h")
            blob_client.upload_blob(h_file_content, overwrite=True)

            print(f"[SUCCESS] Model uploaded. Norm Threshold: {threshold:.6f}")
            self.update_device_twin(threshold, blob_client.url)

        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
        finally:
            if os.path.exists(self.temp_model_path):
                shutil.rmtree(self.temp_model_path)

    def process_event(self, partition_context, event):
        try:
            device_id = event.system_properties.get(b'iothub-connection-device-id').decode()
            if device_id != DEVICE_ID: return
            payload = json.loads(event.body_as_str())
            cmd = payload.get("cmd")
            print(f"Number of buffered samples: {len(self.buffer)} | Received cmd: {cmd}")
            if cmd == "START":
                self.is_calibrating = True
                self.buffer = []
                print("[EVENT] Start Calibration")
            elif cmd == "DATA" and self.is_calibrating:
                vals = payload.get("values")
                if vals: self.buffer.append(vals)
            elif cmd == "STOP" and self.is_calibrating:
                self.is_calibrating = False
                self.train_and_upload()
        except Exception: pass

trainer = AnomalyTrainer()
client = EventHubConsumerClient.from_connection_string(IOTHUB_CONNECTION_STR, consumer_group="$Default", eventhub_name=EVENTHUB_NAME)

with client:
    print("[RUNNING] Listening...")
    client.receive(on_event=trainer.process_event, starting_position="@latest")