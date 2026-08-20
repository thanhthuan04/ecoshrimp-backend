from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import close_mongo_connection, connect_to_mongo
from app.core.env import settings
from app.mqtt.client import start_mqtt_client, stop_mqtt_client
from app.ws.router import router as ws_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    start_mqtt_client()
    yield
    stop_mqtt_client()
    await close_mongo_connection()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "env": settings.ENV}