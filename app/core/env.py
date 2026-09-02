from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENV: str = "development"
    APP_NAME: str = "EcoShrimp Backend"

    API_KEY: str

    MONGO_URI: str
    MONGO_DB_NAME: str = "ecoshrimp"

    MQTT_HOST: str = ""
    MQTT_PORT: int = 8883
    MQTT_USERNAME: str | None = None
    MQTT_PASSWORD: str | None = None
    MQTT_USE_TLS: bool = True
    MQTT_TOPIC_SENSOR: str = "pond1/sensors"
    MQTT_TOPIC_ACTUATOR: str = "pond1/actuators"

    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None

    CORS_ORIGINS: str = "http://localhost:3000"

    SENSOR_LOG_INTERVAL_SECONDS: int = 300

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()