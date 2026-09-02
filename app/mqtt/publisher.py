from app.core.env import settings

_client = None

def set_client(client) -> None:
    global _client
    _client = client

def publish_actuator_command(device: str, state: str) -> None:
    if _client is None:
        raise RuntimeError("MQTT client chưa khởi động.")
    topic = f"{settings.MQTT_TOPIC_ACTUATOR}/{device}"
    mqtt_payload = "1" if state == "ON" else "0"
    _client.publish(topic, mqtt_payload)

def publish_boot_safe_state() -> None:
    publish_actuator_command("pump_out", "OFF")
    publish_actuator_command("aerator", "OFF")
    print("[MQTT] Đã publish trạng thái an toàn lúc khởi động (pump_out, aerator = OFF).")