from fastapi import APIRouter, Form
from typing import Annotated
from config import settings
from app.controllers import askar
import time
import jwt
import uuid

router = APIRouter()


@router.post("/oauth/token", tags=["Authentication"], summary="0Auth 2")
async def oauth(
    client_id: Annotated[str, Form()], client_secret: Annotated[str, Form()]
):
    try:
        client_hash = str(uuid.uuid5(uuid.UUID(client_secret), client_id))
        if not await askar.verify_client_hash(settings.ASKAR_KEY, client_hash):
            return "invalid id"
    except ValueError:
        return "invalid id"
    expires_in = 600
    payload = {"client_id": client_id, "expires": int(time.time()) + expires_in}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return {"access_token": token, "token_type": "Bearer", "expires_in": expires_in}
