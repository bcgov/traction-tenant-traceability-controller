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
    status_list_bitstring_array = BitArray(bin=bitstring)
    status_list_compressed = gzip.compress(status_list_bitstring_array.bytes)
    status_list_encoded = base64.urlsafe_b64encode(status_list_compressed).decode("utf-8").strip('=')
    return status_list_encoded

def bitstring_expand(encoded_list):
    # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-expansion-algorithm
    status_list_compressed = base64.urlsafe_b64decode(encoded_list+'==')
    status_list_bytes = gzip.decompress(status_list_compressed)
    status_list_bit_array = BitArray(bytes=status_list_bytes)
    status_list_bitstring = status_list_bit_array.bin
    return status_list_bitstring

def did_from_label(did_label):
    return f"{settings.DID_WEB_BASE}:{settings.DID_NAMESPACE}:{did_label}"

