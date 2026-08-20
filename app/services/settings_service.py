from app.models.settings import SettingsModel, SettingsUpdate
from app.repositories.settings_repository import get_settings as _get_settings
from app.repositories.settings_repository import update_settings as _update_settings

async def get_current_settings() -> SettingsModel:
    return await _get_settings()

async def apply_settings_update(update: SettingsUpdate) -> SettingsModel:
    changes = update.model_dump(exclude_unset=True)
    return await _update_settings(changes)