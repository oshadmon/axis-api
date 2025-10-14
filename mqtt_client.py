import ast
import random
import paho.mqtt.client as mqtt_client
import queue

class MqttClient:
    def __init__(self, conn:str, topic:str):
        part1, part2 = conn.split("@")
        self.broker, self.port   = part2.split(":")
        self.user, self.password = part1.split(":")
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
        # print(f"\n📨 Message received on {msg.topic}:")
        try:
            content = ast.literal_eval(msg.payload.decode().strip())
        except Exception as error:
            content = msg.payload.decode().strip()
        self.queue.put(content)

