from pydantic import ValidationError

from app.ai.forecast_service import predict as predict_forecast
from app.models.sensor_log import SensorLogCreate, SensorLogModel
from app.repositories.sensor_repository import save_sensor_log
from app.services.alert_service import check_and_alert
from app.services.settings_service import get_current_settings
from app.ws.manager import ws_manager

async def handle_sensor_message(payload: dict) -> None:
    try:
        data = SensorLogCreate(**payload)
    except ValidationError as exc:
        print(f"[MQTT] Payload sensor không hợp lệ: {exc}")
        return

    forecast = predict_forecast(data)
    log_entry = SensorLogModel(**data.model_dump(), forecast=forecast)

    await save_sensor_log(log_entry)
    await ws_manager.broadcast(log_entry.model_dump(mode="json"))

    config = await get_current_settings()
    await check_and_alert(log_entry, config)