from datetime import datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.services.history_service import get_history

router = APIRouter()

@router.get("", summary="Lấy dữ liệu lịch sử theo khung thời gian")
async def read_history(
    range: Literal["day", "week", "month"] = "day",
    date: str | None = Query(None, description="Ngày mốc dạng YYYY-MM-DD, mặc định là hôm nay"),
):
    anchor_date = None
    if date:
        try:
            anchor_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="date phải có định dạng YYYY-MM-DD")

    return await get_history(range, anchor_date)