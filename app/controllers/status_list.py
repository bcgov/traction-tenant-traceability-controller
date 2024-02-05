import requests, random
from config import settings
from datetime import datetime
from bitstring import BitArray
from app.controllers import askar, agent
import gzip, base64


def generate(status_list_bitstring):
    # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-generation-algorithm
    status_list_bitarray = BitArray(bin=status_list_bitstring)
    status_list_compressed = gzip.compress(status_list_bitarray.bytes)
    status_list_encoded = base64.urlsafe_b64encode(status_list_compressed).decode(
        "utf-8"
    )
    return status_list_encoded


def expand(status_list_encoded):
    # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-expansion-algorithm
    status_list_compressed = base64.urlsafe_b64decode(status_list_encoded)
    status_list_bytes = gzip.decompress(status_list_compressed)
    status_list_bitarray = BitArray(bytes=status_list_bytes)
    status_list_bitstring = status_list_bitarray.bin
    return status_list_bitstring


def publish(did, list_id, lenght, list_type="StatusList2021"):
    # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-bitstringstatuslistcredential
    credential = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
        ],
        "id": list_id,
        "issuer": did,
        "issuanceDate": str(datetime.now().isoformat()),
        "type": ["VerifiableCredential"],
        "credentialSubject": {
            "id": f"{list_id}#list",
            "encodedList": generate(str(0) * lenght),
        },
    }
    if list_type == "StatusList2021":
        credential["type"].append("StatusList2021Credential")
        credential["@context"].append("https://w3id.org/vc/status-list/2021/v1")
        credential["credentialSubject"]["type"] = "StatusList2021"
        credential["credentialSubject"]["statusPurpose"] = "revocation"

    elif list_type == "RevocationList2020":
        credential["type"].append("RevocationList2020Credential")
        credential["@context"].append("https://w3id.org/vc-revocation-list-2020/v1")
        credential["credentialSubject"]["type"] = "RevocationList2020"

    options = {
        "verificationMethod": f"{did}#verkey",
        "proofPurpose": "AssertionMethod",
    }
    # TODO, new endpoints
    verkey = agent.get_verkey(did)
    status_list_vc = agent.sign_json_ld(credential, options, verkey)
    return status_list_vc


async def create_entry(label, list_type):
    # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-statuslistcredential
    status_list_id = (
        f"{settings.HTTPS_BASE}/organization/{label}/credentials/status/{list_type}"
    )

    data_key = f"{label}:status_entries:{list_type}"
    status_list_entries = await askar.fetch_data(settings.ASKAR_KEY, data_key)
    # Find an unoccupied index
    list_idx = random.choice(
        [
            e
            for e in range(settings.STATUS_LIST_LENGHT - 1)
            if e not in status_list_entries
        ]
    )
    status_list_entries.append(list_idx)
    await askar.update_data(settings.ASKAR_KEY, data_key, status_list_entries)

    credential_status = {"id": f"{status_list_id}#{list_idx}"}

    if list_type == "RevocationList2020":
        credential_status["type"] = "RevocationList2020Status"
        credential_status["revocationListIndex"] = list_idx
        credential_status["revocationListCredential"] = status_list_id

    elif list_type == "StatusList2021":
        credential_status["type"] = "StatusList2021Entry"
        credential_status["statusPurpose"] = "revocation"
        credential_status["statusListIndex"] = list_idx
        credential_status["statusListCredential"] = status_list_id

    return credential_status


def get_credential_status(vc, status_type):
    # https://www.w3.org/TR/vc-bitstring-status-list/#validate-algorithm
    if status_type == 'RevocationList2020Status':
        status_list_index = vc["credentialStatus"]["revocationListIndex"]
        status_list_credential_endpoint = vc["credentialStatus"]["revocationListCredential"]
    elif status_type == 'StatusList2021Entry':
        status_list_index = vc["credentialStatus"]["statusListIndex"]
        status_list_credential_endpoint = vc["credentialStatus"]["statusListCredential"]

    r = requests.get(status_list_credential_endpoint)
    status_list_vc = r.json()
    status_list_bitstring = expand(status_list_vc["credentialSubject"]["encodedList"])
    status_list = list(status_list_bitstring)
    credential_status_bit = status_list[status_list_index]
    return True if credential_status_bit == "1" else False


async def change_credential_status(vc, status_bit, label, list_type):
    
    if list_type == 'RevocationList2020':
        status_list_index = vc["credentialStatus"]["revocationListIndex"]
    elif list_type == 'StatusList2021':
        status_list_index = vc["credentialStatus"]["statusListIndex"]
        
    data_key = f"{label}:status_lists:{list_type}"
    status_list_vc = await askar.fetch_data(settings.ASKAR_KEY, data_key)
    status_list_encoded = status_list_vc["credentialSubject"]["encodedList"]
    status_list_bitstring = expand(status_list_encoded)
    status_list = list(status_list_bitstring)

    status_list[status_list_index] = status_bit
    status_list_bitstring = "".join(status_list)
    status_list_encoded = generate(status_list_bitstring)

    status_list_vc["credentialSubject"]["encodedList"] = status_list_encoded


    did = vc["issuer"] if isinstance(vc["issuer"], str) else vc["issuer"]["id"]
    verkey = agent.get_verkey(did)
    options = {
        "verificationMethod": f"{did}#verkey",
        "proofPurpose": "AssertionMethod",
    }
    # Remove old proof
    status_list_vc.pop("proof")
    new_status_list_vc = agent.sign_json_ld(status_list_vc, options, verkey)

    return new_status_list_vc
