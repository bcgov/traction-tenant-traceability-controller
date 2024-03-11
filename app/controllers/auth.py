from app.controllers import askar
from config import settings
import uuid
import hashlib
import secrets
from app.validations import ValidationException
from app.auth.handler import decodeJWT


async def verify_client_hash(client_id, client_secret):
    try:
        client_secret_hash = hashlib.sha256(client_secret.encode('utf-8')).hexdigest()
        data_key = f'issuerClients:{client_id}'
        client_data = await askar.fetch_data(settings.ASKAR_PUBLIC_STORE_KEY, data_key)
        if client_data['client_secret_hash'] != client_secret_hash:
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
    client_id = decodeJWT(token)["client_id"]
    data_key = f'issuerClients:{client_id}'
    client_data = await askar.fetch_data(settings.ASKAR_PUBLIC_STORE_KEY, data_key)
    if client_data['did_label'] != did_label:
        raise ValidationException(status_code=401, content={"message": "Unauthorized"})


async def new_issuer_client(did_label):
    client_id = uuid.uuid4()
    client_secret = secrets.token_urlsafe(24)
    client_secret_hash = hashlib.sha256(client_secret.encode('utf-8')).hexdigest()
    client_data = {
        'did_label': did_label,
        'client_secret_hash': client_secret_hash
    }
    data_key = f'issuerClients:{client_id}'
    await askar.store_data(settings.ASKAR_PUBLIC_STORE_KEY, data_key, client_data)

    # Provision private store
    # askarKey = generate_askar_key(client_secret)
    # await askar.provision_store(askarKey)

    return client_id, client_secret
