from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import verify_api_key
from app.mqtt.client import publish_actuator_command
from app.services.settings_service import apply_settings_update
from app.models.settings import SettingsUpdate

router = APIRouter()

DeviceName = Literal["aerator", "pump_in", "pump_out", "light"]
DeviceState = Literal["ON", "OFF"]
SystemMode = Literal["auto", "manual"]

class ControlCommand(BaseModel):
    device: DeviceName
    state: DeviceState

class ModeCommand(BaseModel):
    mode: SystemMode

@router.post("", dependencies=[Depends(verify_api_key)], summary="Điều khiển thiết bị (cần API key)")
async def control_device(command: ControlCommand):
    await apply_settings_update(SettingsUpdate(system_mode="manual"))
    publish_actuator_command(command.device, command.state)
    return {"device": command.device, "state": command.state, "status": "sent"}

@router.post("/mode", dependencies=[Depends(verify_api_key)], summary="Đổi chế độ Tự động/Thủ công")
async def set_system_mode(command: ModeCommand):
    updated = await apply_settings_update(SettingsUpdate(system_mode=command.mode))
    return {"system_mode": updated.system_mode}