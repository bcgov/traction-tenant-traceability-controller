import requests, random
from config import settings
from datetime import datetime
from bitstring import BitArray
from app.validations import ValidationException
from app.controllers import askar
import zlib, base64


def generate(status_list_bitstring):
    # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-generation-algorithm
    status_list_bitarray = BitArray(bin=status_list_bitstring)
    status_list_compressed = zlib.compress(status_list_bitarray.bytes)
    status_list_encoded = base64.standard_b64encode(status_list_compressed).decode(
        "utf-8"
    )
    return status_list_encoded


def expand(status_list_encoded):
    # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-expansion-algorithm
    status_list_compressed = base64.standard_b64decode(status_list_encoded)
    status_list_bytes = zlib.decompress(status_list_compressed)
    status_list_bitarray = BitArray(bytes=status_list_bytes)
    status_list_bitstring = status_list_bitarray.bin
    return status_list_bitstring


def create_credential(issuer, org_label, status_type, status_list_lenght):
    # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-bitstringstatuslistcredential
    status_list_id = f"{settings.HTTPS_BASE}/organization/{org_label}/credentials/status/{status_type}".lower()
    status_list_bitstring = str(0) * status_list_lenght
    status_list_endcoded = generate(status_list_bitstring)
    status_list_credential = {
        "@context": ["https://www.w3.org/ns/credentials/v2"],
        "id": status_list_id,
        "issuer": issuer,
        "validFrom": str(datetime.now().isoformat()),
        "type": ["VerifiableCredential", f"{status_type}Credential"],
        "credentialSubject": {
            "id": f"{status_list_id}#list",
            "type": status_type,
            "encodedList": status_list_endcoded,
        },
    }
    if status_type in ["StatusList2021"]:
        status_list_credential["credentialSubject"]["purpose"] = "revocation"
    return status_list_credential


async def create_entry(org_label, status_type):
    # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-statuslistcredential
    if status_type == "RevocationList2020Status":
        status_list_id = f"{settings.HTTPS_BASE}/organization/{org_label}/credentials/status/RevocationList2020".lower()
    elif status_type == "StatusList2021Entry":
        status_list_id = f"{settings.HTTPS_BASE}/organization/{org_label}/credentials/status/StatusList2021".lower()

    data_key = f"{org_label}:status_entries:{status_list_id}".lower()
    status_list_entries = await askar.fetch_data(settings.ASKAR_KEY, data_key)
    list_idx = random.choice(
        [
            e
            for e in range(settings.STATUS_LIST_LENGHT - 1)
            if e not in status_list_entries
        ]
    )
    status_list_entries.append(list_idx)
    data_key = f"{org_label}:status_entries:{status_list_id}".lower()
    await askar.update_data(settings.ASKAR_KEY, data_key, status_list_entries)

    if status_type == "RevocationList2020Status":
        credential_status = {
            "id": f"{status_list_id}#{list_idx}",
            "type": status_type,
            "revocationListIndex": list_idx,
            "revocationListCredential": status_list_id,
        }
    if status_type == "StatusList2021Entry":
        credential_status = {
            "id": f"{status_list_id}#{list_idx}",
            "type": status_type,
            "statusListIndex": list_idx,
            "statusListCredential": status_list_id,
            "statusPurpose": "revocation",
        }

    return credential_status


def get_credential_status(vc):
    # https://www.w3.org/TR/vc-bitstring-status-list/#validate-algorithm
    if vc["credentialStatus"]["type"] == "RevocationList2020Status":
        status_list_index = vc["credentialStatus"]["revocationListIndex"]
        status_list_credential_endpoint = vc["credentialStatus"][
            "revocationListCredential"
        ]
    elif vc["credentialStatus"]["type"] == "StatusList2021Entry":
        status_list_index = vc["credentialStatus"]["statusListIndex"]
        status_list_credential_endpoint = vc["credentialStatus"]["statusListCredential"]

    r = requests.get(status_list_credential_endpoint)
    status_list_vc = r.json()

    status_list_bitstring = expand(status_list_vc["credentialSubject"]["encodedList"])
    status_list = list(status_list_bitstring)
    credential_status_bit = status_list[status_list_index]
    return True if credential_status_bit == "1" else False


async def change_credential_status(vc, status_bit, org_label):
    if vc["credentialStatus"]["type"] == "RevocationList2020Status":
        status_list_index = vc["credentialStatus"]["revocationListIndex"]
        status_list_id = vc["credentialStatus"]["revocationListCredential"]
    elif vc["credentialStatus"]["type"] == "StatusList2021Entry":
        status_list_index = vc["credentialStatus"]["statusListIndex"]
        status_list_id = vc["credentialStatus"]["statusListCredential"]

    data_key = f"{org_label}:status_lists:{status_list_id}".lower()
    status_list_vc = await askar.fetch_data(settings.ASKAR_KEY, data_key)

    status_list_encoded = status_list_vc["credentialSubject"]["encodedList"]

    status_list_bitstring = expand(status_list_encoded)
    status_list = list(status_list_bitstring)

    status_list[status_list_index] = status_bit
    status_list_bitstring = "".join(status_list)
    status_list_encoded = generate(status_list_bitstring)

    status_list_vc["credentialSubject"]["encodedList"] = status_list_encoded

    # Remove old proof
    status_list_vc.pop("proof")

    return status_list_vc
