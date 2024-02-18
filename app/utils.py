from urllib import parse
import uuid
import secrets
from config import settings
import hashlib
from app.controllers import askar
from aries_askar.bindings import generate_raw_key


def generate_client_hash(client_secret, client_id):
    return str(uuid.uuid5(client_secret, client_id))


def did_from_label(label):
    return f"{settings.DID_WEB_BASE}:organizations:{label}"


def generate_askar_key(seed):
    return generate_raw_key(seed)


async def new_client(label):
    label_hash = hashlib.md5(label.encode())
    client_id = uuid.UUID(label_hash.hexdigest())
    client_secret = secrets.token_urlsafe(24)
    client_hash = str(uuid.uuid5(client_id, client_secret))

    await askar.append_client_hash(settings.ASKAR_KEY, client_hash)
    askar_key = generate_askar_key(client_secret)

    # Provision private store
    # await askar.provision_store(askar_key)

    return client_id, client_secret


async def new_issuer_client(orgId):
    orgIdHash = hashlib.md5(orgId.encode())
    clientId = uuid.UUID(orgIdHash.hexdigest())
    clientSecret = secrets.token_urlsafe(24)
    clientHash = str(uuid.uuid5(clientId, clientSecret))

    await askar.append_client_hash(settings.ASKAR_KEY, clientHash)

    # Provision private store
    # askarKey = generate_askar_key(clientSecret)
    # await askar.provision_store(askarKey)

    return clientId, clientSecret
