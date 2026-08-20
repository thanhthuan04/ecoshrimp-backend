from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.env import settings

class MongoManager:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

mongo_manager = MongoManager()

async def connect_to_mongo() -> None:
    mongo_manager.client = AsyncIOMotorClient(settings.MONGO_URI)
    mongo_manager.db = mongo_manager.client[settings.MONGO_DB_NAME]

    await mongo_manager.client.admin.command("ping")
    print(f"[MongoDB] Đã kết nối tới database '{settings.MONGO_DB_NAME}'")

    await _ensure_indexes()

async def close_mongo_connection() -> None:
    if mongo_manager.client:
        mongo_manager.client.close()
        print("[MongoDB] Đã đóng kết nối.")

async def _ensure_indexes() -> None:
    db = mongo_manager.db
    await db["sensor_logs"].create_index("timestamp")
    await db["alert_logs"].create_index([("timestamp", -1), ("type", 1)])

def get_database() -> AsyncIOMotorDatabase:
    if mongo_manager.db is None:
        raise RuntimeError(
            "MongoDB chưa được kết nối. Kiểm tra lại lifespan trong app/main.py"
        )
    return mongo_manager.db