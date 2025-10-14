import random
import paho.mqtt.client as mqtt_client
import base64
import os
import json

import camera_functions
from __support__ import  validate_timestamp_format, rest_request, sort_timestamps
from camera_functions import list_recordings


# MQTT Broker details
BROKER = "172.104.228.251"
PORT = 1883
USER = "anyloguser"
PASSWORD = "mqtt4AnyLog!"
# TOPIC = "axis/B8A44FC5C075/event/tns:axis/CameraApplicationPlatform/ObjectAnalytics/Device1ScenarioANY"
TOPIC = "power-plant"

# video credentials
BASE_URL = ""
VIDEO_USER = ""
VIDEO_PASSWORD = ""


def snapshot():
    camera_functions.take_snapshot(base_url=BASE_URL, user=VIDEO_USER, password=VIDEO_PASSWORD)
    filepath = os.path.join('../data', 'snapshot.jpg')

    with open(filepath, 'rb') as fwrite:
        encoded_string = base64.b64encode(fwrite.read()).decode("utf-8")

    return encoded_string


def get_video(timestamp:str):
    current_dt = validate_timestamp_format(timestamp)
    if not current_dt:
        return None

    recordings  = list_recordings(base_url=BASE_URL, user=VIDEO_USER, password=VIDEO_PASSWORD)
    recordings = sort_timestamps(recordings)
    recording_id = recordings[0].get('@recordingid')

    for recording in recordings:
        start = validate_timestamp_format(recording.get('@starttimelocal'))
        end = validate_timestamp_format(recording.get('@stoptimelocal'))
        if (start and end) and start <= current_dt <= end:
            recording_id = recording.get('@recordingid')
        elif (start and not end) and  start <= current_dt:
            recording_id = recording.get('@recordingid')

    return recording_id

# for video in list_recordings(base_url=BASE_URL, user=VIDEO_USER, password=VIDEO_PASSWORD):
    #

    #         # content, _, _ = export_recording(base_url=BASE_URL, user=VIDEO_USER, password=VIDEO_PASSWORD, record_id=recording_id)
    #         payload = {
    #             "start_time": video.get('@starttime'),
    #             "end_time": video.get('@stoptime'),
    #             "recording_id": recording_id,
    #             # "video": base64.b64encode(content).decode('utf-8'), # mp4
    #         }
    #         return payload

    # return None


class MqttClient:
    def __init__(self):
        self.client = mqtt_client.Client(client_id=f"mqtt-client-{random.randint(0, 1000)}")
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
        # content = ast.literal_eval(msg.payload.decode().strip())
        content = {
            "topic":"axis:CameraApplicationPlatform/ObjectAnalytics/Device1ScenarioANY",
            "timestamp":1759713693673,
            "serial":"B8A44FC5C075",
            "message":{
                "source":{},
                "key":{},
                "data":{
                    "objectId":"370312",
                    "active":"0",
                    "classTypes":"human",
                    "triggerTime": "2025-10-09T11:57:22.928315-04:00" # "2025-10-09T12:00:33.856-0400"
                }
            }
        }

        # timestamp = content['message']['data']['triggerTime']
        serial = content.get('serial')
        payload = {
            "table": f"camera_{serial}" if serial else "camera_unknown",
            "recording_id": get_video(timestamp=content['message']['data'].get('triggerTime')),
            "timestamp": content.get('timestamp'),
            "object_id": content['message']['data'].get('objectId'),
            "object": content['message']['data'].get('classTypes'),
            "active": True if content['message']['data'].get('active') == 1 else False,
            "snapshot": snapshot(),  # jpg
        }
        # video_payload = get_video(timestamp=content['message']['data']['triggerTime'])
        # if video_payload:
        #     payload.update(video_payload)

        rest_request(method='POST', url='http://173.255.230.238:32149',
                     headers={
                         'command': 'data',
                         'topic': 'axis-new',
                         'User-Agent': 'AnyLog/1.23',
                         'Content-Type': 'text/plain'
                     }, data_payload=json.dumps(payload))

        # exit(1)

if __name__ == "__main__":
    # get_video(timestamp='2025-10-09T11:03:33.344706Z')
    mqtt_client_instance = MqttClient()
    mqtt_client_instance.connect()
