from fastapi import APIRouter, Form
from typing import Annotated
from config import settings
from app.controllers import auth
import time
import jwt

router = APIRouter()


@router.post("/oauth/token", tags=["Authentication"], summary="0Auth 2")
async def oauth(
    client_id: Annotated[str, Form()], client_secret: Annotated[str, Form()]
):
    await auth.verify_client_hash(client_id, client_secret)
    expires_in = 600
    payload = {"client_id": client_id, "expires": int(time.time()) + expires_in}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return {"access_token": token, "token_type": "Bearer", "expires_in": expires_in}
