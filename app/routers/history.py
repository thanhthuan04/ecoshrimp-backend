from typing import Literal

from fastapi import APIRouter

from app.services.history_service import get_history

router = APIRouter()

@router.get("", summary="Lấy dữ liệu lịch sử theo khung thời gian")
async def read_history(range: Literal["day", "week", "month"] = "day"):
    return await get_history(range)