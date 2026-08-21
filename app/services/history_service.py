from datetime import datetime, timedelta

from app.repositories.sensor_repository import get_history_aggregated, get_logs_for_date

_RANGE_CONFIG = {
    "week": {"days_back": 6, "format": "%Y-%m-%dT%H:00"},
    "month": {"days_back": 29, "format": "%Y-%m-%d"},
}

async def get_history(range_key: str, anchor_date: datetime | None = None) -> list[dict]:
    anchor = anchor_date or datetime.utcnow()

    if range_key == "day":
        day_start = anchor.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        raw_points = await get_logs_for_date(day_start, day_end)
        return [
            {
                "timestamp": point["timestamp"].isoformat(),
                "avg_temp": point["temp"],
                "avg_ph": point["ph"],
                "avg_do": point["do"],
                "avg_turbidity": point["turbidity"],
            }
            for point in raw_points
        ]

    config = _RANGE_CONFIG.get(range_key, _RANGE_CONFIG["week"])
    end_date = anchor.replace(hour=23, minute=59, second=59, microsecond=0)
    start_date = end_date - timedelta(days=config["days_back"])

    raw_points = await get_history_aggregated(start_date, end_date, config["format"])

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