from fastapi import APIRouter, Query

from app.services.alert_query_service import list_alerts

router = APIRouter()

@router.get("", summary="Lấy danh sách cảnh báo gần đây")
async def read_alerts(
    limit: int = Query(20, ge=1, le=100, description="Số lượng cảnh báo mỗi trang"),
    skip: int = Query(0, ge=0, description="Số lượng bỏ qua - dùng để phân trang"),
):
    return await list_alerts(limit=limit, skip=skip)