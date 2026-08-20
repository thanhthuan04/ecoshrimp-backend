import httpx

from app.core.env import settings as env_settings
from app.models.alert_log import AlertLogModel, AlertType
from app.models.sensor_log import SensorLogModel
from app.models.settings import SettingsModel
from app.repositories.alert_repository import save_alert_log

_TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"

async def check_and_alert(log_entry: SensorLogModel, config: SettingsModel) -> None:
    checks = [
        (log_entry.do < config.do_danger, AlertType.DO_LOW, log_entry.do, config.do_danger,
         f"DO nguy hiểm: {log_entry.do} mg/L (ngưỡng {config.do_danger})"),
        (not config.temp_min <= log_entry.temp <= config.temp_max, AlertType.TEMP_OUT_OF_RANGE,
         log_entry.temp, config.temp_max, f"Nhiệt độ bất thường: {log_entry.temp}°C"),
        (not config.ph_min <= log_entry.ph <= config.ph_max, AlertType.PH_OUT_OF_RANGE,
         log_entry.ph, config.ph_max, f"pH bất thường: {log_entry.ph}"),
        (log_entry.turbidity > config.turbidity_max, AlertType.TURBIDITY_HIGH,
         log_entry.turbidity, config.turbidity_max, f"Độ đục cao: {log_entry.turbidity} NTU"),
    ]

    for is_triggered, alert_type, value, threshold, message in checks:
        if is_triggered:
            await _send_alert(alert_type, value, threshold, message)

async def _send_alert(alert_type: AlertType, value: float, threshold: float, message: str) -> None:
    sent = await _send_telegram_message(f"⚠️ Cảnh báo ao nuôi: {message}")

    await save_alert_log(
        AlertLogModel(type=alert_type, message=message, value=value, threshold=threshold, sent_telegram=sent)
    )

async def _send_telegram_message(text: str) -> bool:
    if not env_settings.TELEGRAM_BOT_TOKEN or not env_settings.TELEGRAM_CHAT_ID:
        print("[Alert] Thiếu TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID, bỏ qua gửi Telegram.")
        return False

    url = _TELEGRAM_API_URL.format(token=env_settings.TELEGRAM_BOT_TOKEN)
    payload = {"chat_id": env_settings.TELEGRAM_CHAT_ID, "text": text}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        print(f"[Alert] Gửi Telegram thất bại: {exc}")
        return False