from app.core.database import get_database
from app.models.sensor_log import SensorLogModel

async def save_sensor_log(log_entry: SensorLogModel) -> None:
    db = get_database()
    await db["sensor_logs"].insert_one(log_entry.model_dump())

async def get_latest_sensor_log() -> dict | None:
    db = get_database()
    return await db["sensor_logs"].find_one(sort=[("timestamp", -1)])