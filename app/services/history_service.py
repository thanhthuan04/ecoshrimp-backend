from datetime import datetime, timedelta

from app.repositories.sensor_repository import get_history_aggregated

_RANGE_CONFIG = {
    "day": {"delta": timedelta(days=1), "format": "%Y-%m-%dT%H:00"},
    "week": {"delta": timedelta(days=7), "format": "%Y-%m-%dT%H:00"},
    "month": {"delta": timedelta(days=30), "format": "%Y-%m-%d"},
}

async def get_history(range_key: str) -> list[dict]:
    config = _RANGE_CONFIG.get(range_key, _RANGE_CONFIG["day"])
    start_date = datetime.utcnow() - config["delta"]

    raw_points = await get_history_aggregated(start_date, config["format"])

    return [
        {
            "timestamp": point["_id"],
            "avg_temp": round(point["avg_temp"], 2),
            "avg_ph": round(point["avg_ph"], 2),
            "avg_do": round(point["avg_do"], 2),
            "avg_turbidity": round(point["avg_turbidity"], 2),
        }
        for point in raw_points
    ]