from fastapi import APIRouter, Depends

from app.core.security import verify_api_key
from app.models.settings import SettingsModel, SettingsUpdate
from app.services.settings_service import apply_settings_update, get_current_settings

router = APIRouter()

@router.get("", response_model=SettingsModel, summary="Lấy cấu hình hiện tại")
async def read_settings():
    return await get_current_settings()

@router.patch(
    "",
    response_model=SettingsModel,
    dependencies=[Depends(verify_api_key)],
    summary="Cập nhật cấu hình (cần API key)",
)
async def update_settings(update: SettingsUpdate):
    return await apply_settings_update(update)