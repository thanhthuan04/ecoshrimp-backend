from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import verify_api_key
from app.mqtt.client import publish_actuator_command

router = APIRouter()

DeviceName = Literal["aerator", "pump_in", "pump_out", "light"]
DeviceState = Literal["ON", "OFF"]

class ControlCommand(BaseModel):
    device: DeviceName
    state: DeviceState

@router.post("", dependencies=[Depends(verify_api_key)])
async def control_device(command: ControlCommand):
    publish_actuator_command(command.device, command.state)
    return {"device": command.device, "state": command.state, "status": "sent"}