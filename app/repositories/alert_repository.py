from app.core.database import get_database
from app.models.alert_log import AlertLogModel

async def save_alert_log(alert: AlertLogModel) -> None:
    db = get_database()
    await db["alert_logs"].insert_one(alert.model_dump())

async def get_alert_logs(limit: int = 20, skip: int = 0) -> list[dict]:
    db = get_database()
    cursor = db["alert_logs"].find().sort("timestamp", -1).skip(skip).limit(limit)
    return [doc async for doc in cursor]

async def count_alert_logs() -> int:
    db = get_database()
    return await db["alert_logs"].count_documents({})