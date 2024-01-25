import time
from typing import Dict
from config import settings
import jwt, hashlib
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")
def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header == settings.TRACEABILITY_ADMIN_API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API Key",
    )

def token_response(token: str, expires: int):
    return {"access_token": token, "expires": expires}


def signJWT(client_id: str) -> Dict[str, str]:
    payload = {"client_id": client_id, "expires": int(time.time()) + 600}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return token_response(token, payload["expires"])


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return decoded_token if decoded_token["expires"] >= int(time.time()) else None
    except:
        return {}


def is_authorized(token: str, label: str):
    decoded_token = decodeJWT(token)
    if decoded_token['client_id'] != hashlib.md5(label.encode()).hexdigest():
        return False
    return True
