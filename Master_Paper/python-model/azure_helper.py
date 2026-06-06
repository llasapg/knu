import os
import time
import struct
import requests
from datetime import datetime, timezone, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from dotenv import load_dotenv

load_dotenv()

DEVICE_ID = os.getenv("DEVICE_ID", "test_1")
BLOB_CONN_STR = os.getenv("BLOB_CONN_STR")
NET_SERVICE_URL = os.getenv("NET_SERVICE_URL", "http://localhost:5000/api/iot/update-twin")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")
IOTHUB_CONNECTION_STR = os.getenv("IOTHUB_CONNECTION_STR")

def _generate_sas_url(blob_service_client, container_name, blob_name, expiry_days=365):
    """Generate a SAS URL with read access valid for expiry_days."""
    account_name = blob_service_client.account_name
    account_key  = blob_service_client.credential.account_key
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(days=expiry_days)
    )
    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

def upload_model_to_blob(tflite_model_bytes, device_id, threshold, min_vals, max_vals):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)

        container_name = "models"
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()

        # Upload C header file (legacy / debugging)
        h_file_content = bytes_to_c_array(tflite_model_bytes, threshold, min_vals, max_vals)
        blob_h = blob_service_client.get_blob_client(container=container_name, blob=f"{device_id}/model_data.h")
        blob_h.upload_blob(h_file_content, overwrite=True)

        # Upload binary model for OTA download by device
        # Format: [uint32 model_len][model bytes][float threshold][float*3 min_vals][float*3 max_vals]
        binary_content = struct.pack('<I', len(tflite_model_bytes))
        binary_content += tflite_model_bytes
        binary_content += struct.pack('<f', threshold)
        binary_content += struct.pack('<3f', *min_vals)
        binary_content += struct.pack('<3f', *max_vals)

        blob_bin = blob_service_client.get_blob_client(container=container_name, blob=f"{device_id}/model.bin")
        blob_bin.upload_blob(binary_content, overwrite=True)

        # Generate SAS URL (1 year) so the device can download without public access
        sas_url = _generate_sas_url(blob_service_client, container_name, f"{device_id}/model.bin")
        print(f"[SUCCESS] Model uploaded to Blob for {device_id} (h + bin)")
        return sas_url
    except Exception as e:
        print(f"[ERROR] Blob upload failed: {e}")
        return None

def bytes_to_c_array(data, threshold, min_vals, max_vals, var_name="smartiot_model"):
    hex_data = [f"0x{b:02x}" for b in data]
    c_code = f"#ifndef MODEL_DATA_H\n#define MODEL_DATA_H\n\n"
    c_code += f"unsigned char {var_name}[] = {{\n  "
    c_code += ", ".join(hex_data)
    c_code += f"\n}};\n\nunsigned int {var_name}_len = {len(data)};\n"
    c_code += f"float {var_name}_threshold = {threshold:.6f};\n"

    # --- ДОБАВЛЯЕМ МАССИВЫ МИНИМУМОВ И МАКСИМУМОВ ---
    min_str = ", ".join([f"{v:.6f}" for v in min_vals])
    max_str = ", ".join([f"{v:.6f}" for v in max_vals])
    c_code += f"float {var_name}_min_vals[] = {{{min_str}}};\n"
    c_code += f"float {var_name}_max_vals[] = {{{max_str}}};\n\n"

    c_code += f"#endif"
    return c_code

def update_device_twin(device_id, threshold, model_sas_url, min_vals=None, max_vals=None):
    try:
        payload = {
            "deviceId": device_id,
            "threshold": float(threshold),
            "modelUrl": model_sas_url,
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