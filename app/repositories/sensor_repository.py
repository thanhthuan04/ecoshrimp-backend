from app.core.database import get_database
from app.models.sensor_log import SensorLogModel

async def save_sensor_log(log_entry: SensorLogModel) -> None:
    db = get_database()
    await db["sensor_logs"].insert_one(log_entry.model_dump())

async def get_latest_sensor_log() -> dict | None:
    db = get_database()
    return await db["sensor_logs"].find_one(sort=[("timestamp", -1)])

async def get_history_aggregated(start_date, date_format: str) -> list[dict]:
    db = get_database()
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date}}},
        {
            "$group": {
                "_id": {"$dateToString": {"format": date_format, "date": "$timestamp"}},
                "avg_temp": {"$avg": "$temp"},
                "avg_ph": {"$avg": "$ph"},
                "avg_do": {"$avg": "$do"},
                "avg_turbidity": {"$avg": "$turbidity"},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    cursor = db["sensor_logs"].aggregate(pipeline)
    return [doc async for doc in cursor]