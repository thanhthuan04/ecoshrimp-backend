from app.models.sensor_log import ForecastData
from app.models.settings import SettingsModel
from app.mqtt.client import publish_actuator_command

async def run_automation(forecast: ForecastData, config: SettingsModel) -> None:
    if config.system_mode != "auto":
        return

    if config.auto_aerator:
        _decide_aerator(forecast, config)

    if config.auto_pump_in or config.auto_pump_out:
        _decide_pump(forecast, config)

def _decide_aerator(forecast: ForecastData, config: SettingsModel) -> None:
    should_run = forecast.future_do < config.do_danger
    publish_actuator_command("aerator", "ON" if should_run else "OFF")

def _decide_pump(forecast: ForecastData, config: SettingsModel) -> None:
    ph_low = forecast.future_ph < config.ph_min
    turbidity_high = forecast.future_turbidity > config.turbidity_max

    should_pump_in = ph_low or turbidity_high

    if config.auto_pump_in:
        publish_actuator_command("pump_in", "ON" if should_pump_in else "OFF")

    if config.auto_pump_out:
        should_pump_out = not should_pump_in
        publish_actuator_command("pump_out", "ON" if should_pump_out else "OFF")