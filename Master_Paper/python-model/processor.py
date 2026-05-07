import os
import json
from sqlite3 import Date
import trainer
import azure_helper
from datetime import datetime

DEVICE_ID = azure_helper.DEVICE_ID

class EventProcessor:
    def __init__(self, sequence_length=10, features=3):
        self.buffer = []
        self.is_calibrating = False
        self.seq_len = sequence_length
        self.features = features
        self.temp_model_path = "temp_smartiot_export"
        self.min_vals = None
        self.max_vals = None

    def process_event(self, partition_context, event):
        now = datetime.now()
        try:
            device_id = event.system_properties.get(b'iothub-connection-device-id').decode()
            if device_id != DEVICE_ID:
                print(f"[!] Ignored event from device: {device_id}")
                return
            payload = json.loads(event.body_as_str())
            cmd = payload.get("cmd")
            print(f"{now}[EVENT] Received cmd: {cmd} from device: {device_id}")
            print(f"Number of buffered samples: {len(self.buffer)} | Received cmd: {cmd}")
            if cmd == "START":
                self.is_calibrating = True
                self.buffer = []
                print(f"{now}[EVENT] Start Calibration")
            elif cmd == "DATA" and self.is_calibrating:
                vals = payload.get("values")
                if vals:
                    self.buffer.append(vals)
                print(f"{now}[EVENT] Buffered data. Current buffer size: {len(self.buffer)}")
            elif cmd == "STOP" and self.is_calibrating:
                self.is_calibrating = False
                trainer.train_and_upload(self)
        except Exception as e:
            print(f"{now}[ERROR] process_event failed: {e}")