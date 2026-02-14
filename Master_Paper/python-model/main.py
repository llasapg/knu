import os
import processor
import azure_helper
from azure.eventhub import EventHubConsumerClient

DEVICE_ID = azure_helper.DEVICE_ID
EVENTHUB_NAME = azure_helper.EVENTHUB_NAME
IOTHUB_CONNECTION_STR = azure_helper.IOTHUB_CONNECTION_STR

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

processor = processor.EventProcessor()
client = EventHubConsumerClient.from_connection_string(IOTHUB_CONNECTION_STR, consumer_group="$Default", eventhub_name=EVENTHUB_NAME)

with client:
    print("[RUNNING] Listening...")
    client.receive(on_event=processor.process_event, starting_position="@latest")