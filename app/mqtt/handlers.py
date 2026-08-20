from pydantic import ValidationError

from app.models.sensor_log import SensorLogCreate, SensorLogModel
from app.repositories.sensor_repository import save_sensor_log
from app.ws.manager import ws_manager

async def handle_sensor_message(payload: dict) -> None:
    try:
        data = SensorLogCreate(**payload)
    except ValidationError as exc:
        print(f"[MQTT] Payload sensor không hợp lệ: {exc}")
        return

    log_entry = SensorLogModel(**data.model_dump())

    await save_sensor_log(log_entry)
    await ws_manager.broadcast(log_entry.model_dump(mode="json"))