import requests, random
from config import settings
from datetime import datetime
from bitstring import BitArray
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


def create_credential(did, list_id, lenght):
    # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-bitstringstatuslistcredential
    credential = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://w3id.org/vc/status-list/2021/v1",
            ],
        "id": list_id,
        "issuer": did,
        "issuanceDate": str(datetime.now().isoformat()),
        "type": ["VerifiableCredential", "StatusList2021Credential"],
        "credentialSubject": {
            "id": f"{list_id}#list",
            "type": "StatusList2021",
            "encodedList": generate(str(0) * lenght),
            "statusPurpose": "revocation"
        }
    }
    return credential


async def create_entry(org_label):
    # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-statuslistcredential
    status_list_id = f"{settings.HTTPS_BASE}/organization/{org_label}/credentials/status/revocation"

    data_key = f"{org_label}:status_entries".lower()
    status_list_entries = await askar.fetch_data(settings.ASKAR_KEY, data_key)
    list_idx = random.choice(
        [
            e
            for e in range(settings.STATUS_LIST_LENGHT - 1)
            if e not in status_list_entries
        ]
    )
    status_list_entries.append(list_idx)
    data_key = f"{org_label}:status_entries".lower()
    await askar.update_data(settings.ASKAR_KEY, data_key, status_list_entries)
    credential_status = {
        "id": f"{status_list_id}#{list_idx}",
        "type": "StatusList2021Entry",
        "statusListIndex": list_idx,
        "statusListCredential": status_list_id,
        "statusPurpose": "revocation",
    }

    return credential_status


def get_credential_status(vc):
    # https://www.w3.org/TR/vc-bitstring-status-list/#validate-algorithm
    status_list_credential_endpoint = vc["credentialStatus"]["statusListCredential"]

    r = requests.get(status_list_credential_endpoint)
    status_list_vc = r.json()

    status_list_bitstring = expand(status_list_vc["credentialSubject"]["encodedList"])
    status_list = list(status_list_bitstring)
    status_list_index = vc["credentialStatus"]["statusListIndex"]
    credential_status_bit = status_list[status_list_index]
    return True if credential_status_bit == "1" else False


async def change_credential_status(vc, status_bit, org_label):
    data_key = f"{org_label}:status_list".lower()
    status_list_vc = await askar.fetch_data(settings.ASKAR_KEY, data_key)
    
    status_list_encoded = status_list_vc["credentialSubject"]["encodedList"]
    status_list_bitstring = expand(status_list_encoded)
    status_list = list(status_list_bitstring)
    
    status_list_index = vc["credentialStatus"]["statusListIndex"]
    status_list[status_list_index] = status_bit
    status_list_bitstring = "".join(status_list)
    status_list_encoded = generate(status_list_bitstring)

    status_list_vc["credentialSubject"]["encodedList"] = status_list_encoded

    # Remove old proof
    status_list_vc.pop("proof")

    return status_list_vc
