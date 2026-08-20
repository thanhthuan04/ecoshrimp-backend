from datetime import datetime
from pydantic import BaseModel, Field

class ForecastData(BaseModel):
    future_do: float
    future_temp: float
    future_ph: float
    future_turbidity: float

class SensorLogModel(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    temp: float
    ph: float
    do: float
    turbidity: float
    level: int = 1
    forecast: ForecastData | None = None

class SensorLogCreate(BaseModel):
    temp: float
    ph: float
    do: float
    turbidity: float
    level: int = 1