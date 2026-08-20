from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class AlertType(str, Enum):
    DO_LOW = "do_low"
    TEMP_OUT_OF_RANGE = "temp_out_of_range"
    PH_OUT_OF_RANGE = "ph_out_of_range"
    TURBIDITY_HIGH = "turbidity_high"
    AI_EARLY_WARNING = "ai_early_warning"

class AlertLogModel(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: AlertType
    message: str
    value: float
    threshold: float
    sent_telegram: bool = False