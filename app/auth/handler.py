import time
from typing import Dict
from config import settings
import jwt


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
