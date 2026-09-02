import json
import random
import sys
import time
from pathlib import Path

import paho.mqtt.client as mqtt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.core.env import settings

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

if settings.MQTT_USERNAME:
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

if settings.MQTT_USE_TLS:
    client.tls_set()

try:
    client.connect(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=60)
    print(f"Đã kết nối với MQTT Broker: {settings.MQTT_HOST}:{settings.MQTT_PORT}")
except Exception as e:
    print(f"Không thể kết nối MQTT: {e}")
    print("Kiểm tra lại MQTT_HOST/MQTT_USERNAME/MQTT_PASSWORD trong .env đã điền chưa.")
    sys.exit(1)

client.loop_start()

do_val = 5.0
temp_val = 30.0
ph_val = 7.8
turbidity_val = 10.0

print(f"Bắt đầu gửi dữ liệu giả lập lên topic '{settings.MQTT_TOPIC_SENSOR}'...")
try:
    while True:
        do_val += random.uniform(-0.1, 0.1)
        temp_val += random.uniform(-0.2, 0.2)
        ph_val += random.uniform(-0.05, 0.05)
        turbidity_val += random.uniform(-0.5, 0.5)

        payload = {
            "temp": round(temp_val, 2),
            "ph": round(ph_val, 2),
            "do": round(do_val, 2),
            "turbidity": round(turbidity_val, 2),
            "level": 1,
        }

        client.publish(settings.MQTT_TOPIC_SENSOR, json.dumps(payload))
        print(f"Gửi: {payload}")
        time.sleep(2)
except KeyboardInterrupt:
    print("\nDừng giả lập.")
finally:
    client.loop_stop()
    client.disconnect()