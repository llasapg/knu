import os
import requests
import urllib.parse
import time
import hmac
import hashlib
import base64
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()

EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")
DEVICE_ID = os.getenv("DEVICE_ID", "test_1")
IOTHUB_CONNECTION_STR = os.getenv("IOTHUB_CONNECTION_STR")
IOTHUB_SERVICE_STR = os.getenv("IOTHUB_SERVICE_STR")
BLOB_CONN_STR = os.getenv("BLOB_CONN_STR")

def generate_sas_token(uri, key, policy_name, expiry=3600):
    ttl = int(time.time()) + expiry
    encoded_uri = urllib.parse.quote(uri, safe='')
    string_to_sign = f"{encoded_uri}\n{ttl}"
    decoded_key = base64.b64decode(key)
    signature = hmac.new(decoded_key, string_to_sign.encode('utf-8'), hashlib.sha256).digest()
    encoded_sig = base64.b64encode(signature).decode('utf-8')
    url_encoded_sig = urllib.parse.quote(encoded_sig, safe='')
    return f"SharedAccessSignature sr={encoded_uri}&sig={url_encoded_sig}&se={ttl}&skn={policy_name}"

def upload_model_to_blob(tflite_model_bytes, model_bytes, device_id, threshold):
    h_file_content = bytes_to_c_array(tflite_model_bytes, threshold)
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
    blob_client = blob_service_client.get_blob_client(container="models", blob=f"{DEVICE_ID}/model_data.h")
    blob_client.upload_blob(h_file_content, overwrite=True)

def bytes_to_c_array(data, threshold, var_name="smartiot_model"):
    hex_data = [f"0x{b:02x}" for b in data]
    c_code = f"#ifndef MODEL_DATA_H\n#define MODEL_DATA_H\n\nunsigned char {var_name}[] = {{\n  "
    c_code += ", ".join(hex_data)
    c_code += f"\n}};\n\nunsigned int {var_name}_len = {len(data)};\n"
    c_code += f"float {var_name}_threshold = {threshold:.6f};\n\n#endif"
    return c_code

def update_device_twin(device_id, threshold, min_vals=None, max_vals=None):
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
    blob_client = blob_service_client.get_blob_client(container="models", blob=f"{DEVICE_ID}/model_data.h")
    try:
        if IOTHUB_SERVICE_STR is None:
            raise ValueError("IOTHUB_SERVICE_STR environment variable is not set")

        parts = dict(item.split('=', 1) for item in IOTHUB_SERVICE_STR.split(';'))
        host = parts['HostName'].strip()
        key_name = parts['SharedAccessKeyName'].strip()
        key_val = parts['SharedAccessKey'].strip()

        resource_uri = f"{host}/devices/{device_id}"
        token = generate_sas_token(resource_uri, key_val, key_name)

        url = f"https://{host}/devices/{device_id}/twin?api-version=2020-03-13"

        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        patch = {
            "properties": {
                "desired": {
                    "model_threshold": float(threshold),
                    "model_url": blob_client.url,
                    "min_vals": min_vals if min_vals is not None else [],
                    "max_vals": max_vals if max_vals is not None else []
                }
            }
        }

        print(f"[*] Sending update to Twin: {url}")
        response = requests.patch(url, json=patch, headers=headers)

        if response.status_code in [200, 204]:
            print(f"[SUCCESS] Device Twin updated for {device_id}")
        else:
            print(f"[ERROR] Twin update failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"[ERROR] REST update failed: {e}")