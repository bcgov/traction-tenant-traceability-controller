from urllib import parse
import uuid
import secrets
from config import settings
import hashlib
from hashlib import sha256
from app.controllers import askar
from aries_askar.bindings import generate_raw_key
from bitstring import BitArray
import gzip, base64


def generate_client_hash(client_secret, client_id):
    return str(uuid.uuid5(client_secret, client_id))

def bitstring_generate(bitstring):
    # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-generation-algorithm
    statusListBitarray = BitArray(bin=bitstring)
    statusListCompressed = gzip.compress(statusListBitarray.bytes)
    statusList_encoded = base64.urlsafe_b64encode(statusListCompressed).decode("utf-8")
    return statusList_encoded

def bitstring_expand(encoded_list):
    # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-expansion-algorithm
    statusListCompressed = base64.urlsafe_b64decode(encoded_list)
    statusListBytes = gzip.decompress(statusListCompressed)
    statusListBitarray = BitArray(bytes=statusListBytes)
    statusListBitstring = statusListBitarray.bin
    return statusListBitstring

def did_from_label(did_label):
    return f"{settings.DID_WEB_BASE}:{settings.DID_NAMESPACE}:{did_label}"


def generate_askar_key(seed):
    return generate_raw_key(seed)


async def new_client(did_label):
    did_label_hash = hashlib.md5(did_label.encode())
    client_id = uuid.UUID(did_label_hash.hexdigest())
    client_secret = secrets.token_urlsafe(24)
    client_hash = str(uuid.uuid5(client_id, client_secret))

    await askar.append_client_hash(settings.ASKAR_PUBLIC_STORE_KEY, client_hash)
    # askar_key = generate_askar_key(client_secret)

    # Provision private store
    # await askar.provision_store(askar_key)

    return client_id, client_secret


async def new_issuer_client(did_label):
    client_id = uuid.uuid4()
    client_secret = secrets.token_urlsafe(24)
    client_secret_hash = sha256(client_secret.encode('utf-8')).hexdigest()
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
