from app.controllers.askar import AskarController
from config import settings
import uuid
import hashlib
import secrets
from app.validations import ValidationException
from app.auth.handler import decodeJWT
from app.utils import did_from_label


def can_issue(credential, did_label):
    """Function to check if the issuer field matches the organization's instance"""
    did = (
        credential["issuer"]
        if isinstance(credential["issuer"], str)
        else credential["issuer"]["id"]
    )
    if did != did_from_label(did_label):
        raise ValidationException(
            status_code=400, content={"message": "Invalid issuer"}
        )
    return did


async def verify_client_hash(client_id, client_secret):
    try:
        client_hash = uuid.uuid5(uuid.UUID(client_id), client_secret)
        if await AskarController().fetch(f'clientHash:{client_id}') != str(client_hash):
            raise ValidationException(
                status_code=400,
                content={"message": "Invalid client"},
            )
    except ValueError:
        raise ValidationException(
            status_code=400,
            content={"message": "Invalid client"},
        )


async def is_authorized(did_label, request):
    token = request.headers.get("Authorization").replace("Bearer ", "")
    request_client_id = decodeJWT(token)["client_id"]
    stored_client_id = await AskarController(db=did_label).fetch('clientId')
    if request_client_id != stored_client_id:
        raise ValidationException(status_code=401, content={"message": "Unauthorized"})


async def new_issuer_client(did_label):
    client_id = uuid.uuid4()
    client_secret = secrets.token_urlsafe(24)
    client_hash = uuid.uuid5(client_id, client_secret)
    await AskarController().store(f'clientHash:{str(client_id)}', str(client_hash))
    await AskarController(db=did_label).store('clientId', str(client_id))

    return str(client_id), client_secret
