import requests, random
from config import settings
from datetime import datetime
from bitstring import BitArray
from app.controllers import askar, agent, did_web
from app.validations import ValidationException
import gzip, base64


def generate(statusListBitstring):
    # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-generation-algorithm
    statusListBitarray = BitArray(bin=statusListBitstring)
    statusListCompressed = gzip.compress(statusListBitarray.bytes)
    statusList_encoded = base64.urlsafe_b64encode(statusListCompressed).decode(
        "utf-8"
    )
    return statusList_encoded


def expand(statusListEncoded):
    # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-expansion-algorithm
    statusListCompressed = base64.urlsafe_b64decode(statusListEncoded)
    statusListBytes = gzip.decompress(statusListCompressed)
    statusListBitarray = BitArray(bytes=statusListBytes)
    statusListBitstring = statusListBitarray.bin
    return statusListBitstring


async def create(orgId, statusType, purpose="revocation"):
    did = did_web.from_org_id(orgId)
    # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-bitstringstatuslistcredential
    credential = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
        ],
        "issuer": did,
        "issuanceDate": str(datetime.now().isoformat()),
        "type": ["VerifiableCredential"],
        "credentialSubject": {
            "type": statusType, 
            "encodedList": generate(str(0) * settings.STATUS_LIST_LENGHT),
        },
    }
    if statusType == "StatusList2021":
        credential["@context"].append("https://w3id.org/vc/status-list/2021/v1")
        credential["type"].append("StatusList2021Credential")
        credential["credentialSubject"]["statusPurpose"] = purpose

    elif statusType == "RevocationList2020":
        credential["@context"].append("https://w3id.org/vc-revocation-list-2020/v1")
        credential["type"].append("RevocationList2020Credential")

    options = {
        "verificationMethod": f"{did}#verkey",
        "proofPurpose": "AssertionMethod",
    }
    # TODO, new endpoints for issuance
    verkey = agent.get_verkey(did)
    statusCredential = agent.sign_json_ld(credential, options, verkey)
    statusCredentialId = statusType
    
    dataKey = askar.statusCredentialDataKey(orgId, statusCredentialId)
    await askar.store_data(settings.ASKAR_KEY, dataKey, statusCredential)
    
    dataKey = askar.statusEntriesDataKey(orgId, statusCredentialId)
    await askar.store_data(
        settings.ASKAR_KEY, dataKey, [0, settings.STATUS_LIST_LENGHT - 1]
    )


async def create_entry(orgId, statusListCredentialId, purpose="revocation"):
    # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-statuslistcredential

    dataKey = askar.statusEntriesDataKey(orgId, statusListCredentialId)
    statusListEntries = await askar.fetch_data(settings.ASKAR_KEY, dataKey)
    # Find an unoccupied index
    statusListIndex = random.choice(
        [
            e
            for e in range(settings.STATUS_LIST_LENGHT - 1)
            if e not in statusListEntries
        ]
    )
    statusListEntries.append(statusListIndex)
    await askar.update_data(settings.ASKAR_KEY, dataKey, statusListEntries)

    listType = statusListCredentialId
    statusListCredentialId = (
        f"{settings.HTTPS_BASE}/organizations/{orgId}/credentials/status/{statusListCredentialId}"
    )
    credentialStatus = {"id": f"{statusListCredentialId}#{statusListIndex}"}

    if listType == "RevocationList2020":
        credentialStatus["type"] = "RevocationList2020Status"
        credentialStatus["revocationListIndex"] = statusListIndex
        credentialStatus["revocationListCredential"] = statusListCredentialId

    elif listType == "StatusList2021":
        credentialStatus["type"] = "StatusList2021Entry"
        credentialStatus["statusPurpose"] = purpose
        credentialStatus["statusListIndex"] = statusListIndex
        credentialStatus["statusListCredential"] = statusListCredentialId

    return credentialStatus

async def add_credential_status(orgId, credential, status):
    if status["type"] == "StatusList2021Entry":
        credential["@context"].append("https://w3id.org/vc/status-list/2021/v1")
        credential["credentialStatus"] = await create_entry(
            orgId, "StatusList2021"
        )
    elif status["type"] == "RevocationList2020Status":
        credential["@context"].append("https://w3id.org/vc-revocation-list-2020/v1")
        credential["credentialStatus"] = await create_entry(
            orgId, "RevocationList2020"
        )
    return credential


def get_credential_status(vc, statusType):
    # https://www.w3.org/TR/vc-bitstring-status-list/#validate-algorithm
    if statusType == "RevocationList2020Status":
        statusListIndex = vc["credentialStatus"]["revocationListIndex"]
        statusListCredentialUri = vc["credentialStatus"][
            "revocationListCredential"
        ]
    elif statusType == "StatusList2021Entry":
        statusListIndex = vc["credentialStatus"]["statusListIndex"]
        statusListCredentialUri = vc["credentialStatus"]["statusListCredential"]

    r = requests.get(statusListCredentialUri)
    statusListCredential = r.json()
    statusListBitstring = expand(statusListCredential["credentialSubject"]["encodedList"])
    statusList = list(statusListBitstring)
    credentialStatusBit = statusList[statusListIndex]
    return True if credentialStatusBit == "1" else False


async def change_credential_status(vc, statusBit, orgId, statusListCredentialId):
    if statusListCredentialId == "RevocationList2020":
        statusList_index = vc["credentialStatus"]["revocationListIndex"]
    elif statusListCredentialId == "StatusList2021":
        statusList_index = vc["credentialStatus"]["statusListIndex"]

    dataKey = askar.statusCredentialDataKey(orgId, statusListCredentialId)
    statusListCredential = await askar.fetch_data(settings.ASKAR_KEY, dataKey)
    statusListEncoded = statusListCredential["credentialSubject"]["encodedList"]
    statusListBitstring = expand(statusListEncoded)
    statusList = list(statusListBitstring)

    statusList[statusList_index] = statusBit
    statusListBitstring = "".join(statusList)
    statusListEncoded = generate(statusListBitstring)

    statusListCredential["credentialSubject"]["encodedList"] = statusListEncoded

    did = vc["issuer"] if isinstance(vc["issuer"], str) else vc["issuer"]["id"]
    verkey = agent.get_verkey(did)
    options = {
        "verificationMethod": f"{did}#verkey",
        "proofPurpose": "AssertionMethod",
    }
    # Remove old proof
    statusListCredential.pop("proof")
    statusListCredential = agent.sign_json_ld(statusListCredential, options, verkey)

    return statusListCredential

async def get_status_list_credential(orgId, statusListCredentialId):
    try:
        dataKey = askar.statusCredentialDataKey(orgId, statusListCredentialId)
        statusListCredential = await askar.fetch_data(settings.ASKAR_KEY, dataKey)
    except:
        return ValidationException(
            status_code=404,
            content={"message": "Status list not found"},
        )
    return statusListCredential