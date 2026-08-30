from app.models.sensor_log import ForecastData
from app.models.settings import SettingsModel
from app.mqtt.client import publish_actuator_command

_TEMP_LOW_THRESHOLD = 22.0
_PH_LOW_THRESHOLD = 6.5

async def run_automation(forecast: ForecastData, config: SettingsModel) -> None:
    if config.system_mode != "auto":
        return

    if config.auto_aerator:
        _decide_aerator(forecast, config)

    if config.auto_pump_in or config.auto_pump_out or config.auto_aerator:
        _decide_light(forecast, config)

    if config.auto_pump_in or config.auto_pump_out:
        _decide_pump(forecast, config)

def _decide_aerator(forecast: ForecastData, config: SettingsModel) -> None:
    should_run = forecast.future_do < config.do_danger
    publish_actuator_command("aerator", "ON" if should_run else "OFF")

def _decide_light(forecast: ForecastData, config: SettingsModel) -> None:
    temp_too_cold = forecast.future_temp < _TEMP_LOW_THRESHOLD
    temp_out_of_range = not config.temp_min <= forecast.future_temp <= config.temp_max

    should_run = temp_out_of_range and temp_too_cold
    publish_actuator_command("light", "ON" if should_run else "OFF")

def _decide_pump(forecast: ForecastData, config: SettingsModel) -> None:
    temp_out_of_range = not config.temp_min <= forecast.future_temp <= config.temp_max
    temp_too_cold = forecast.future_temp < _TEMP_LOW_THRESHOLD
    temp_wants_pump_in = temp_out_of_range and not temp_too_cold

    ph_out_of_range = not config.ph_min <= forecast.future_ph <= config.ph_max
    ph_too_low = forecast.future_ph < _PH_LOW_THRESHOLD
    ph_wants_pump_in = ph_out_of_range and ph_too_low
    ph_wants_pump_out = ph_out_of_range and not ph_too_low

    turbidity_out_of_range = not config.turbidity_min <= forecast.future_turbidity <= config.turbidity_max
    turbidity_too_low = forecast.future_turbidity < config.turbidity_min
    turbidity_wants_pump_in = turbidity_out_of_range and turbidity_too_low
    turbidity_wants_pump_out = turbidity_out_of_range and not turbidity_too_low

    should_pump_in = temp_wants_pump_in or ph_wants_pump_in or turbidity_wants_pump_in
    should_pump_out = ph_wants_pump_out or turbidity_wants_pump_out

    if config.auto_pump_in:
        publish_actuator_command("pump_in", "ON" if should_pump_in else "OFF")

    if config.auto_pump_out:
        publish_actuator_command("pump_out", "ON" if should_pump_out else "OFF")