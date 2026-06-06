"""
One-time script: regenerate SAS URL for existing model.bin and patch device twin.
Run once: python patch_twin_sas.py
"""
import azure_helper
from azure.storage.blob import BlobServiceClient

DEVICE_ID = azure_helper.DEVICE_ID
BLOB_CONN_STR = azure_helper.BLOB_CONN_STR

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
sas_url = azure_helper._generate_sas_url(blob_service_client, "models", f"{DEVICE_ID}/model.bin")
print(f"[SAS] {sas_url}")

azure_helper.update_device_twin(
    device_id=DEVICE_ID,
    threshold=0.0648894965648651,  # current value from twin
    model_sas_url=sas_url
)
print("[DONE] Twin patched with SAS URL")

