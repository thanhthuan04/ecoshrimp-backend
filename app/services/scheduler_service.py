import asyncio
from datetime import datetime

from app.models.settings import SettingsModel, TimerConfig
from app.mqtt.publisher import publish_actuator_command
from app.services.settings_service import get_current_settings

_CHECK_INTERVAL_SECONDS = 60

_TIMER_DEVICE_MAP: list[tuple[str, str]] = [
    ("timer_aerator", "aerator"),
    ("timer_pump_in", "pump_in"),
    ("timer_pump_out", "pump_out"),
    ("timer_light", "light"),
]

def _is_within_window(timer: TimerConfig, current_time: str) -> bool:
    if not timer.enabled or timer.start == timer.end:
        return False
    if timer.start <= timer.end:
        return timer.start <= current_time <= timer.end
    return current_time >= timer.start or current_time <= timer.end

async def _tick() -> None:
    config: SettingsModel = await get_current_settings()
    current_time = datetime.now().strftime("%H:%M")

    for field_name, device in _TIMER_DEVICE_MAP:
        timer: TimerConfig = getattr(config, field_name)
        if _is_within_window(timer, current_time):
            publish_actuator_command(device, "ON")

async def start_scheduler_loop() -> None:
    while True:
        try:
            await _tick()
        except Exception as exc:
            print(f"[Scheduler] Lỗi khi kiểm tra timer: {exc}")
        await asyncio.sleep(_CHECK_INTERVAL_SECONDS)