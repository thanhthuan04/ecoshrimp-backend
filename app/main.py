import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import close_mongo_connection, connect_to_mongo
from app.core.env import settings
from app.mqtt.client import start_mqtt_client, stop_mqtt_client
from app.routers.control import router as control_router
from app.routers.history import router as history_router
from app.routers.settings import router as settings_router
from app.services.scheduler_service import start_scheduler_loop
from app.ws.router import router as ws_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    start_mqtt_client()
    scheduler_task = asyncio.create_task(start_scheduler_loop())
    yield
    scheduler_task.cancel()
    stop_mqtt_client()
    await close_mongo_connection()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description=(
        "API giám sát và điều khiển ao nuôi tôm realtime: dữ liệu cảm biến qua MQTT, "
        "dự báo AI, lịch sử, cấu hình ngưỡng, và điều khiển thiết bị. "
        "Xem chi tiết từng endpoint bên dưới (Swagger UI)."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router)
app.include_router(settings_router, prefix="/api/settings", tags=["settings"])
app.include_router(history_router, prefix="/api/history", tags=["history"])
app.include_router(control_router, prefix="/api/control", tags=["control"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "env": settings.ENV}