from urllib import parse
import uuid
from config import settings
import hashlib


def format_label(label):
    # Remove spacing and lowercase
    return parse.quote(label.strip().lower())


def generate_client_hash(client_secret, client_id):
    return str(uuid.uuid5(client_secret, client_id))


def did_from_label(label):
    label = format_label(label)
    return f"{settings.DID_WEB_BASE}:organization:{label}"


def new_client(label):
    label = format_label(label)
    client_id = hashlib.md5(label.encode()).hexdigest()
    client_secret = uuid.uuid4()
    client_hash = generate_client_hash(client_secret, client_id)
    return client_id, client_secret, client_hash
