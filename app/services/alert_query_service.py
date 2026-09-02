from app.repositories.alert_repository import count_alert_logs, get_alert_logs

async def list_alerts(limit: int = 20, skip: int = 0) -> dict:
    logs = await get_alert_logs(limit=limit, skip=skip)
    total = await count_alert_logs()

    return {
        "items": [
            {
                "timestamp": log["timestamp"].isoformat(),
                "type": log["type"],
                "message": log["message"],
                "value": log["value"],
                "threshold": log["threshold"],
                "sent_telegram": log["sent_telegram"],
            }
            for log in logs
        ],
        "total": total,
    }