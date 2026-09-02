from typing import Literal

from pydantic import BaseModel

class TimerConfig(BaseModel):
    enabled: bool = False
    start: str = ""
    end: str = ""

class SettingsModel(BaseModel):
    system_mode: Literal["auto", "manual"] = "manual"

    farm_location: str = "Đà Nẵng"

    do_danger: float = 4.0
    ai_early_warning: int = 30
    temp_max: float = 35.0
    temp_min: float = 22.0
    ph_max: float = 9.0
    ph_min: float = 6.5
    turbidity_max: float = 70.0
    turbidity_min: float = 20.0

    temp_low_threshold: float = 22.0
    ph_low_threshold: float = 6.5

    auto_aerator: bool = False
    auto_pump_in: bool = False
    auto_pump_out: bool = False
    auto_light: bool = False

    timer_aerator: TimerConfig = TimerConfig()
    timer_pump_in: TimerConfig = TimerConfig()
    timer_pump_out: TimerConfig = TimerConfig()
    timer_light: TimerConfig = TimerConfig()

class SettingsUpdate(BaseModel):
    system_mode: Literal["auto", "manual"] | None = None
    farm_location: str | None = None
    do_danger: float | None = None
    ai_early_warning: int | None = None
    temp_max: float | None = None
    temp_min: float | None = None
    ph_max: float | None = None
    ph_min: float | None = None
    turbidity_max: float | None = None
    turbidity_min: float | None = None
    temp_low_threshold: float | None = None
    ph_low_threshold: float | None = None
    auto_aerator: bool | None = None
    auto_pump_in: bool | None = None
    auto_pump_out: bool | None = None
    auto_light: bool | None = None
    timer_aerator: TimerConfig | None = None
    timer_pump_in: TimerConfig | None = None
    timer_pump_out: TimerConfig | None = None
    timer_light: TimerConfig | None = None