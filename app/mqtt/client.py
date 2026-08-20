import asyncio
import json

import paho.mqtt.client as mqtt

from app.core.env import settings
from app.mqtt.handlers import handle_sensor_message

_main_loop: asyncio.AbstractEventLoop | None = None
_client: mqtt.Client | None = None

def _on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("[MQTT] Kết nối thành công tới broker.")
        client.subscribe(settings.MQTT_TOPIC_SENSOR)
    else:
        print(f"[MQTT] Kết nối thất bại, reason_code={reason_code}")

def _on_disconnect(client, userdata, reason_code, properties=None):
    print(f"[MQTT] Mất kết nối (reason_code={reason_code}). paho sẽ tự reconnect.")

def _on_message(client, userdata, msg):
    if _main_loop is None:
        return
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"[MQTT] Payload không hợp lệ trên topic {msg.topic}: {exc}")
        return

    asyncio.run_coroutine_threadsafe(handle_sensor_message(payload), _main_loop)

def start_mqtt_client() -> None:
    global _client, _main_loop
    _main_loop = asyncio.get_event_loop()

    _client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    if settings.MQTT_USERNAME:
        _client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

    if settings.MQTT_USE_TLS:
        _client.tls_set()

    _client.on_connect = _on_connect
    _client.on_disconnect = _on_disconnect
    _client.on_message = _on_message

    _client.reconnect_delay_set(min_delay=1, max_delay=30)

    _client.connect_async(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=60)
    _client.loop_start()

def stop_mqtt_client() -> None:
    if _client:
        _client.loop_stop()
        _client.disconnect()
        print("[MQTT] Đã ngắt kết nối.")

def publish_actuator_command(device: str, state: str) -> None:
    if _client is None:
        raise RuntimeError("MQTT client chưa khởi động.")
    topic = f"{settings.MQTT_TOPIC_ACTUATOR}/{device}"
    _client.publish(topic, state)