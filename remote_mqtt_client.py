import ast
import random
import paho.mqtt.client as mqtt_client
import queue

from __support__ import extract_credentials

class MqttClient:
    def __init__(self, conn:str, topic:str):
        self.broker, self.user, self.password = extract_credentials(conn)
        self.broker, self.port   = self.broker.split(":")
        self.topic = topic
        try:
            self.port = int(self.port)
        except Exception as error:
            raise Exception(f"Failed to set PORT as integer value (Error: {error})")

        self.queue = queue.Queue()


        self.client = mqtt_client.Client(client_id=f"mqtt-client-{random.randint(0, 1000)}")
        self.client.username_pw_set(self.user, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        try:
            self.client.connect(self.broker, self.port)
            print(f"✅ Connected to {self.broker}:{self.port}")
            self.client.loop_start()  # ✅ run MQTT in background
            # self.client.loop_forever()
        except Exception as error:
            raise Exception(f"❌ Failed to connect to {self.broker}:{self.port} — {error}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("🚀 Connected successfully!")
            client.subscribe(self.topic)
            print(f"📡 Subscribed to topic: {self.topic}")
        else:
            print(f"❌ Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            content = ast.literal_eval(msg.payload.decode().strip())
        except Exception:
            content = msg.payload.decode().strip()
        self.queue.put(content)


def mqtt_publish(conn:str, topic:str, message:str):
    broker, port = conn.split(":")
    port = int(port)
    try:
        client = mqtt_client.Client()
        client.connect(host=broker, port=port,  keepalive=60)
        result = client.publish(topic=topic, payload=message, qos=0)
        result.wait_for_publish()
        client.disconnect()
    except Exception as error:
        raise Exception(f"Failed to execute MQTT publish against {broker}:{port} (Error: {error})")
