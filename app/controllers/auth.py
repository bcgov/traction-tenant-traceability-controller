from app.controllers import askar
from config import settings
import uuid
import hashlib
from app.validations import ValidationException
from app.auth.handler import decodeJWT


async def verify_client_hash(clientId, clientSecret):
    try:
        clientHash = str(uuid.uuid5(uuid.UUID(clientId), clientSecret))
        if not await askar.verify_client_hash(settings.ASKAR_KEY, clientHash):
            raise ValidationException(
                status_code=400,
                content={"message": "Invalid client"},
            )
    except ValueError:
        raise ValidationException(
            status_code=400,
            content={"message": "Invalid client"},
        )


async def is_authorized(orgId, request):
    token = request.headers.get("Authorization").replace("Bearer ", "")
    decodedToken = decodeJWT(token)
    labelHash = hashlib.md5(orgId.encode())
    clientId = str(uuid.UUID(labelHash.hexdigest()))
    if decodedToken["client_id"] != clientId:
        raise ValidationException(status_code=401, content={"message": "Unauthorized"})