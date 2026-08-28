from app.core.database import get_database
from app.models.sensor_log import SensorLogModel

async def save_sensor_log(log_entry: SensorLogModel) -> None:
    db = get_database()
    await db["sensor_logs"].insert_one(log_entry.model_dump())

async def get_latest_sensor_log() -> dict | None:
    db = get_database()
    return await db["sensor_logs"].find_one(sort=[("timestamp", -1)])

async def get_logs_for_date(start_date, end_date) -> list[dict]:
    db = get_database()
    cursor = db["sensor_logs"].find({"timestamp": {"$gte": start_date, "$lte": end_date}}).sort("timestamp", 1)
    return [doc async for doc in cursor]