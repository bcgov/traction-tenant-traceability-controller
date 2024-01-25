from fastapi import APIRouter, Form
from typing import Annotated
from config import settings
from app.auth import handler
from app.controllers import agent
from app.validations import ValidationException
import hashlib
from time import time

router = APIRouter()


@router.post("/oauth/token", tags=["Authentication"], summary="0Auth 2")
async def oauth(
    client_id: Annotated[str, Form()], client_secret: Annotated[str, Form()]
):
    if (
        client_id == settings.TRACTION_TENANT_ID
        and client_secret == settings.TRACTION_API_KEY
    ):
        token = agent.request_token(client_id, client_secret)
        # token = handler.signJWT(token)
        # We need an expiration
        token = {
            "token_type": "Bearer",
            "access_token": token,
            # "expires_in": 600,
        }
        return token
    raise ValidationException(
        status_code=401,
        content={"message": "Unauthorized"},
    )
