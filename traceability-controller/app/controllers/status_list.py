import requests, random
from config import settings
from datetime import datetime
from bitstring import BitArray
from app.controllers import askar, agent, did_web
from app.controllers.traction import TractionController
from app.controllers.askar import AskarController
from app.validations import ValidationException
from app.utils import did_from_label
import gzip, base64
import uuid

class StatusListController:
    def __init__(self, did_label):
        self.did_label = did_label
        self.issuer = did_from_label(did_label)
        self.lenght = settings.STATUS_LIST_LENGHT
        self.status_endpoint = f"{settings.HTTPS_BASE}/{settings.DID_NAMESPACE}/{did_label}/credentials/status"

    def generate(self, bitstring):
        # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-generation-algorithm
        statusListBitarray = BitArray(bin=bitstring)
        statusListCompressed = gzip.compress(statusListBitarray.bytes)
        statusList_encoded = base64.urlsafe_b64encode(statusListCompressed).decode("utf-8")
        return statusList_encoded


    def expand(self, encoded_list):
        # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-expansion-algorithm
        statusListCompressed = base64.urlsafe_b64decode(encoded_list)
        statusListBytes = gzip.decompress(statusListCompressed)
        statusListBitarray = BitArray(bytes=statusListBytes)
        statusListBitstring = statusListBitarray.bin
        return statusListBitstring


    async def create(self, purpose="revocation"):
        # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-bitstringstatuslistcredential
        status_list_credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://w3id.org/vc/status-list/2021/v1"
            ],
            "id": f'{self.status_endpoint}/{uuid.uuid4()}',
            "issuer": self.issuer,
            "issuanceDate": str(datetime.now().isoformat()),
            "type": ["VerifiableCredential", "StatusList2021Credential"],
            "credentialSubject": {
                "type": "StatusList2021",
                "encodedList": self.generate(str(0) * self.lenght),
                "statusPurpose": purpose
            },
        }
        status_list_vc = await TractionController(self.did_label).sign_json_ld(status_list_credential)

        await AskarController(self.did_label).store('statusListCredential', status_list_vc)
        await AskarController(self.did_label).store('statusListEntries', [0, self.lenght - 1])


    async def create_entry(self, status):
        # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-statuslistcredential
        askar = AskarController(self.did_label)
        status_entries = await askar.fetch('statusEntries')
        # Find an unoccupied index
        status_index = random.choice(
            [
                e
                for e in range(self.lenght - 1)
                if e not in status_entries
            ]
        )
        status_entries.append(status_index)
        await askar.update('statusEntries', status_entries)
        status_credential = await askar.fetch('statusCredential')['id']

        credential_status_id = status_credential['id']
        credential_status = {
            'id': f'{credential_status_id}#{status_index}',
            'type': 'StatusList2021Entry',
            'statusPurpose': status['statusPurpose'],
            'statusListIndex': status_index,
            'statusListCredential': status_credential['id']
        }

        return credential_status


    def get_credential_status(self, vc, statusType):
        # https://www.w3.org/TR/vc-bitstring-status-list/#validate-algorithm
        statusListIndex = vc["credentialStatus"]["statusListIndex"]
        statusListCredentialUri = vc["credentialStatus"]["statusListCredential"]

        r = requests.get(statusListCredentialUri)
        statusListCredential = r.json()
        statusListBitstring = self.expand(
            statusListCredential["credentialSubject"]["encodedList"]
        )
        statusList = list(statusListBitstring)
        credentialStatusBit = statusList[statusListIndex]
        return True if credentialStatusBit == "1" else False


    async def change_credential_status(self, vc, statusBit, did_label, statusListCredentialId):
        statusList_index = vc["credentialStatus"]["statusListIndex"]

        dataKey = askar.statusCredentialDataKey(did_label, statusListCredentialId)
        statusListCredential = await askar.fetch_data(settings.ASKAR_PUBLIC_STORE_KEY, dataKey)
        statusListEncoded = statusListCredential["credentialSubject"]["encodedList"]
        statusListBitstring = self.expand(statusListEncoded)
        statusList = list(statusListBitstring)

        statusList[statusList_index] = statusBit
        statusListBitstring = "".join(statusList)
        statusListEncoded = self.generate(statusListBitstring)

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


async def get_status_list_credential(did_label, statusListCredentialId):
    try:
        dataKey = askar.statusCredentialDataKey(did_label, statusListCredentialId)
        statusListCredential = await askar.fetch_data(settings.ASKAR_PUBLIC_STORE_KEY, dataKey)
    except:
        return ValidationException(
            status_code=404,
            content={"message": "Status list not found"},
        )
    return statusListCredential
