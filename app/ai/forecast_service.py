from pathlib import Path

import joblib
import numpy as np

from app.models.sensor_log import ForecastData, SensorLogCreate

MODEL_PATH = Path(__file__).resolve().parent / "models" / "pond_forecaster_xgb_latest.pkl"

_SMOOTHING_WEIGHT_PREDICTED = 0.85
_SMOOTHING_WEIGHT_CURRENT = 0.15

_model = None

def _get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Không tìm thấy model tại {MODEL_PATH}. Chạy ml/train_forecaster.py trước."
            )
        _model = joblib.load(MODEL_PATH)
    return _model

def predict(data: SensorLogCreate) -> ForecastData:
    model = _get_model()

    features = np.array([[data.do, data.temp, data.ph, data.turbidity]])
    raw_prediction = model.predict(features)[0]

    smoothed = _smooth(raw_prediction, current=[data.do, data.temp, data.ph, data.turbidity])

    return ForecastData(
        future_do=smoothed[0],
        future_temp=smoothed[1],
        future_ph=smoothed[2],
        future_turbidity=smoothed[3],
    )

def _smooth(predicted: np.ndarray, current: list[float]) -> np.ndarray:
    current_arr = np.array(current)
    return _SMOOTHING_WEIGHT_PREDICTED * predicted + _SMOOTHING_WEIGHT_CURRENT * current_arr