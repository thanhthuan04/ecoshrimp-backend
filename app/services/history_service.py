from datetime import datetime, timedelta

from app.repositories.sensor_repository import get_logs_for_date

_RANGE_DAYS_BACK = {
    "day": 0,
    "week": 6,
    "month": 29,
}

async def get_history(range_key: str, anchor_date: datetime | None = None) -> list[dict]:
    anchor = anchor_date or datetime.utcnow()
    days_back = _RANGE_DAYS_BACK.get(range_key, 0)

    end_date = anchor.replace(hour=23, minute=59, second=59, microsecond=0)
    start_date = (end_date - timedelta(days=days_back)).replace(hour=0, minute=0, second=0, microsecond=0)

    raw_points = await get_logs_for_date(start_date, end_date)

    return [
        {
            "timestamp": point["timestamp"].isoformat(),
            "temp": point["temp"],
            "ph": point["ph"],
            "do": point["do"],
            "turbidity": point["turbidity"],
        }
        for point in raw_points
    ]