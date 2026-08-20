from app.core.database import get_database
from app.models.alert_log import AlertLogModel

async def save_alert_log(alert: AlertLogModel) -> None:
    db = get_database()
    await db["alert_logs"].insert_one(alert.model_dump())