import sys
from pathlib import Path

import paho.mqtt.client as mqtt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.core.env import settings

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected with result code {reason_code}", flush=True)
    topic = f"{settings.MQTT_TOPIC_ACTUATOR}/#"
    client.subscribe(topic)
    print(f"Đang lắng nghe topic: {topic}")

def on_message(client, userdata, msg):
    print(f"{msg.topic} -> {msg.payload.decode()}", flush=True)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

if settings.MQTT_USERNAME:
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

if settings.MQTT_USE_TLS:
    client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

client.connect(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=60)
client.loop_forever()