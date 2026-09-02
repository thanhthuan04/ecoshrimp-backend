from datetime import datetime, timedelta

from pydantic import ValidationError

from app.ai.forecast_service import predict as predict_forecast
from app.core.env import settings
from app.models.sensor_log import SensorLogCreate, SensorLogModel
from app.repositories.sensor_repository import save_sensor_log
from app.services.alert_service import check_and_alert
from app.services.automation_service import run_automation
from app.services.settings_service import get_current_settings
from app.ws.manager import ws_manager

_last_saved_at: datetime | None = None

def _normalize_water_level(raw_level: int) -> bool:
    return raw_level == 1

async def handle_sensor_message(payload: dict) -> None:
    global _last_saved_at

    try:
        data = SensorLogCreate(**payload)
    except ValidationError as exc:
        print(f"[MQTT] Payload sensor không hợp lệ: {exc}")
        return

    forecast = predict_forecast(data)
    is_water_normal = _normalize_water_level(data.level)
    log_entry = SensorLogModel(
        **data.model_dump(exclude={"level"}), level=is_water_normal, forecast=forecast
    )

    await ws_manager.broadcast(log_entry.model_dump(mode="json"))

    config = await get_current_settings()
    await check_and_alert(log_entry, config)
    await run_automation(forecast, config)

    now = datetime.utcnow()
    interval = timedelta(seconds=settings.SENSOR_LOG_INTERVAL_SECONDS)
    if _last_saved_at is None or now - _last_saved_at >= interval:
        await save_sensor_log(log_entry)
        _last_saved_at = now