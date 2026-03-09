import os
import time
import requests
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

DEVICE_ID = os.getenv("DEVICE_ID", "test_1")
BLOB_CONN_STR = os.getenv("BLOB_CONN_STR")
NET_SERVICE_URL = os.getenv("NET_SERVICE_URL", "http://localhost:5000/api/iot/update-twin")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")
IOTHUB_CONNECTION_STR = os.getenv("IOTHUB_CONNECTION_STR")

def upload_model_to_blob(tflite_model_bytes, device_id, threshold):
    try:
        h_file_content = bytes_to_c_array(tflite_model_bytes, threshold)
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)

        container_name = "models"
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()

        blob_name = f"{device_id}/model_data.h"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        blob_client.upload_blob(h_file_content, overwrite=True)

        print(f"[SUCCESS] Model uploaded to Blob for {device_id}")
        return blob_client.url
    except Exception as e:
        print(f"[ERROR] Blob upload failed: {e}")
        return None

def bytes_to_c_array(data, threshold, var_name="smartiot_model"):
    hex_data = [f"0x{b:02x}" for b in data]
    c_code = f"#ifndef MODEL_DATA_H\n#define MODEL_DATA_H\n\n"
    c_code += f"unsigned char {var_name}[] = {{\n  "
    c_code += ", ".join(hex_data)
    c_code += f"\n}};\n\nunsigned int {var_name}_len = {len(data)};\n"
    c_code += f"float {var_name}_threshold = {threshold:.6f};\n\n#endif"
    return c_code

def update_device_twin(device_id, threshold, min_vals=None, max_vals=None):
    try:
        storage_name = BLOB_CONN_STR.split('AccountName=')[1].split(';')[0]
        model_url = f"https://{storage_name}.blob.core.windows.net/models/{device_id}/model_data.h"

        payload = {
            "deviceId": device_id,
            "threshold": float(threshold),
            "modelUrl": model_url,
            "minVals": list(min_vals) if min_vals is not None else [],
            "maxVals": list(max_vals) if max_vals is not None else []
        }

        print(f"[*] Sending update to .NET service: {NET_SERVICE_URL}")
        response = requests.post(NET_SERVICE_URL, json=payload, timeout=10)

        if response.status_code == 200:
            print(f"[SUCCESS] .NET service accepted twin update for {device_id}")
        else:
            print(f"[ERROR] .NET service failed ({response.status_code}): {response.text}")

    except Exception as e:
        print(f"[ERROR] Could not trigger twin update via .NET: {e}")