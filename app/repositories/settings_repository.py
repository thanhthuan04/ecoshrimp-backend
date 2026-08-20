from app.core.database import get_database
from app.models.settings import SettingsModel

_SETTINGS_DOC_ID = "global"

async def get_settings() -> SettingsModel:
    db = get_database()
    doc = await db["settings"].find_one({"_id": _SETTINGS_DOC_ID})
    if doc is None:
        default_settings = SettingsModel()
        await db["settings"].insert_one({"_id": _SETTINGS_DOC_ID, **default_settings.model_dump()})
        return default_settings
    doc.pop("_id", None)
    return SettingsModel(**doc)

async def update_settings(update: dict) -> SettingsModel:
    db = get_database()
    await db["settings"].update_one(
        {"_id": _SETTINGS_DOC_ID},
        {"$set": update},
        upsert=True,
    )
    return await get_settings()