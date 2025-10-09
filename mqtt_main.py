import random
import paho.mqtt.client as mqtt_client
import ast
import base64

import anylog_support
from __support__ import  validate_timestamp_format
from camera_functions import list_recordings, export_recording


# MQTT Broker details
BROKER = "172.104.228.251"
PORT = 1883
USER = "anyloguser"
PASSWORD = "mqtt4AnyLog!"
TOPIC = "power-plant"
CLIENT_ID = f"mqtt-client-{random.randint(0, 1000)}"

# video credentials
BASE_URL = "166.143.227.89"
VIDEO_USER = "AnyLog"
VIDEO_PASSWORD = "OriIsTheBest#1!"


def get_video(timestamp:str):
    current_timestamp = validate_timestamp_format(timestamp)

    all_videos = list_recordings(base_url=BASE_URL, user=VIDEO_USER, password=VIDEO_PASSWORD)
    for video in all_videos:
        start_time = validate_timestamp_format(timestamp=video['@starttime'])
        end_time = validate_timestamp_format(timestamp=video['@stoptime'])

        if start_time <= current_timestamp <= end_time:
            recording_info = {
                "video_id": video['@recordingid'],
                "start_time": video['@starttime'],
                "end_time": video['@stoptime'],
                "source": video['@source'],
                "video_resolution": video['video']['@resolution'],
                "video_width": video['video']['@width'],
                "video_height": video['video']['@height']
            }
            content, _, _ = export_recording(base_url=BASE_URL, user=VIDEO_USER, password=VIDEO_PASSWORD, record_id=video['@recordingid'])
            recording_info['content'] = base64.b64encode(content).decode('utf-8')
            recording_info['file_type'] = 'mp4'
            return recording_info
    return None


class MqttClient:
    def __init__(self):
        self.client = mqtt_client.Client(client_id=CLIENT_ID)
        self.client.username_pw_set(USER, PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        try:
            self.client.connect(BROKER, PORT)
            print(f"✅ Connected to {BROKER}:{PORT}")
            self.client.loop_forever()
        except Exception as error:
            raise Exception(f"❌ Failed to connect to {BROKER}:{PORT} — {error}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("🚀 Connected successfully!")
            client.subscribe(TOPIC)
            print(f"📡 Subscribed to topic: {TOPIC}")
        else:
            print(f"❌ Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        print(f"\n📨 Message received on {msg.topic}:")
        content = ast.literal_eval(msg.payload.decode().strip())
        recording_info = get_video(timestamp='2025-10-09T11:03:33.344706Z')
        exit(1)

if __name__ == "__main__":
    # get_video(timestamp='2025-10-09T11:03:33.344706Z')
    mqtt_client_instance = MqttClient()
    mqtt_client_instance.connect()
