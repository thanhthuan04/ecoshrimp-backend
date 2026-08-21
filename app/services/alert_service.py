import httpx

from app.core.env import settings as env_settings
from app.models.alert_log import AlertLogModel, AlertType
from app.models.sensor_log import ForecastData, SensorLogModel
from app.models.settings import SettingsModel
from app.repositories.alert_repository import save_alert_log

_TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"

async def check_and_alert(log_entry: SensorLogModel, config: SettingsModel) -> None:
    do_triggered = log_entry.do < config.do_danger
    temp_triggered = not config.temp_min <= log_entry.temp <= config.temp_max
    ph_triggered = not config.ph_min <= log_entry.ph <= config.ph_max
    turbidity_triggered = log_entry.turbidity > config.turbidity_max

    current_checks = [
        (do_triggered, AlertType.DO_LOW, log_entry.do, config.do_danger,
         f"DO nguy hiểm: {log_entry.do} mg/L (ngưỡng {config.do_danger})"),
        (temp_triggered, AlertType.TEMP_OUT_OF_RANGE,
         log_entry.temp, config.temp_max, f"Nhiệt độ bất thường: {log_entry.temp}°C"),
        (ph_triggered, AlertType.PH_OUT_OF_RANGE,
         log_entry.ph, config.ph_max, f"pH bất thường: {log_entry.ph}"),
        (turbidity_triggered, AlertType.TURBIDITY_HIGH,
         log_entry.turbidity, config.turbidity_max, f"Độ đục cao: {log_entry.turbidity} NTU"),
    ]

    for is_triggered, alert_type, value, threshold, message in current_checks:
        if is_triggered:
            await _send_alert(alert_type, value, threshold, message)

    if log_entry.forecast:
        already_triggered = {
            "do": do_triggered,
            "temp": temp_triggered,
            "ph": ph_triggered,
            "turbidity": turbidity_triggered,
        }
        await _check_early_warning(log_entry.forecast, config, already_triggered)

async def _check_early_warning(
    forecast: ForecastData, config: SettingsModel, already_triggered: dict[str, bool]
) -> None:
    lead_time = config.ai_early_warning

    early_checks = [
        (not already_triggered["do"] and forecast.future_do < config.do_danger,
         forecast.future_do, config.do_danger,
         f"Dự báo AI: DO sắp xuống mức nguy hiểm trong ~{lead_time} phút tới "
         f"({forecast.future_do:.2f} mg/L)"),
        (not already_triggered["temp"] and not config.temp_min <= forecast.future_temp <= config.temp_max,
         forecast.future_temp, config.temp_max,
         f"Dự báo AI: nhiệt độ sắp bất thường trong ~{lead_time} phút tới "
         f"({forecast.future_temp:.2f}°C)"),
        (not already_triggered["ph"] and not config.ph_min <= forecast.future_ph <= config.ph_max,
         forecast.future_ph, config.ph_max,
         f"Dự báo AI: pH sắp bất thường trong ~{lead_time} phút tới "
         f"({forecast.future_ph:.2f})"),
        (not already_triggered["turbidity"] and forecast.future_turbidity > config.turbidity_max,
         forecast.future_turbidity, config.turbidity_max,
         f"Dự báo AI: độ đục sắp vượt ngưỡng trong ~{lead_time} phút tới "
         f"({forecast.future_turbidity:.2f} NTU)"),
    ]

    for is_triggered, value, threshold, message in early_checks:
        if is_triggered:
            await _send_alert(AlertType.AI_EARLY_WARNING, value, threshold, message)

async def _send_alert(alert_type: AlertType, value: float, threshold: float, message: str) -> None:
    icon = "🔮" if alert_type == AlertType.AI_EARLY_WARNING else "⚠️"
    sent = await _send_telegram_message(f"{icon} Cảnh báo ao nuôi: {message}")

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