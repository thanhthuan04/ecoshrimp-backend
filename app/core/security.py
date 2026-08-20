import secrets

from fastapi import Header, HTTPException, status

from app.core.env import settings

async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> None:
    if not secrets.compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key không hợp lệ.",
        )