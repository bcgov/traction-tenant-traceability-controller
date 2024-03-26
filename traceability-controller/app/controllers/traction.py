import requests
from config import settings
from app.models.did_document import DidDocument
from app.controllers.askar import AskarController
from app.utils import did_from_label, bitstring_generate, bitstring_expand
from app.validations import ValidationException
from app.validations import valid_did
from datetime import datetime
import uuid
import random

class TractionController:
    def __init__(self, did_label):
        self.endpoint = settings.TRACTION_API_ENDPOINT
        self.tenant_id = settings.TRACTION_TENANT_ID
        self.api_key = settings.TRACTION_API_KEY
        self.did_label = did_label
        self.did = did_from_label(did_label)
        
        endpoint = f"{self.endpoint}/multitenancy/tenant/{self.tenant_id}/token"
        body = {"api_key": self.api_key}
        r = requests.post(endpoint, json=body)
        try:
            token = r.json()["token"]
            self.headers = {"Authorization": f"Bearer {token}"}
        except:
            raise ValidationException(
                status_code=r.status_code, content={"message": r.text}
            )

    def verify_token(self, token):
        headers = {"Authorization": token}
        endpoint = f"{self.endpoint}/tenant"
        r = requests.get(endpoint, headers=headers)
        try:
            return r.json()
        except:
            raise ValidationException(
                status_code=r.status_code, content={"message": r.text}
            )

    async def create_did(self, did_method='sov', key_type='ed25519'):
        
        # Create keypair
        endpoint = f"{self.endpoint}/wallet/did/create"
        body = {"method": did_method, "options": {"key_type": key_type, "did": self.did}}
        r = requests.post(endpoint, headers=self.headers, json=body)
        try:
            verkey = r.json()["result"]["verkey"]
            # Provision askar db and store verkey 
            await AskarController(self.did_label).provision()
            await AskarController(self.did_label).store('verkey', verkey)
        except:
            raise ValidationException(
                status_code=r.status_code, content={"message": r.text}
            )
            
    async def create_status_list(self, purpose='revocation'):
        status_endpoint = f'{settings.HTTPS_BASE}/{settings.DID_NAMESPACE}/{self.did_label}/credentials/status'
        status_list_credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://w3id.org/vc/status-list/2021/v1"
            ],
            "id": f'{status_endpoint}/{uuid.uuid4()}',
            "issuer": self.did,
            "issuanceDate": str(datetime.now().isoformat()),
            "type": ["VerifiableCredential", "StatusList2021Credential"],
            "credentialSubject": {
                "type": "StatusList2021",
                "encodedList": bitstring_generate(str(0) * settings.STATUS_LIST_LENGHT),
                "statusPurpose": purpose
            },
        }
        status_list_vc = await self.sign_json_ld(status_list_credential)
        status_entries = [0, settings.STATUS_LIST_LENGHT - 1]

        await AskarController(self.did_label).store('statusListCredential', status_list_vc)
        await AskarController(self.did_label).store('statusListEntries', status_entries)
            
    async def create_status_entry(self, purpose='revocation'):
        # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-statuslistcredential
        status_entries = await AskarController(self.did_label).fetch('statusListEntries')
        # Find an unoccupied index
        status_index = random.choice(
            [
                e
                for e in range(settings.STATUS_LIST_LENGHT - 1)
                if e not in status_entries
            ]
        )
        status_entries.append(status_index)
        await AskarController(self.did_label).update('statusListEntries', status_entries)
        status_credential = await AskarController(self.did_label).fetch('statusListCredential')

        credential_status_id = status_credential['id']
        credential_status = {
            'id': f'{credential_status_id}#{status_index}',
            'type': 'StatusList2021Entry',
            'statusPurpose': purpose,
            'statusListIndex': status_index,
            'statusListCredential': status_credential['id']
        }
        return credential_status
    
    async def get_status_list_credential(self):
        try:
            return await AskarController(self.did_label).fetch('statusListCredential')
        except:
            return ValidationException(
                status_code=404,
                content={"message": "Status list not found"},
            )


    def get_credential_status(self, vc):
        # https://www.w3.org/TR/vc-bitstring-status-list/#validate-algorithm
        status_index = vc["credentialStatus"]["statusListIndex"]
        status_list_endpoint = vc["credentialStatus"]["statusListCredential"]

        r = requests.get(status_list_endpoint)
        status_list_vc = r.json()
        status_list_bitstring = bitstring_expand(
            status_list_vc["credentialSubject"]["encodedList"]
        )
        status_list = list(status_list_bitstring)
        status_bit = status_list[status_index]
        return True if status_bit == "1" else False

    def resolve_did(self, did):
        # TODO, improve did validation
        if did[:9] == "urn:uuid:":
            raise ValidationException(status_code=404, content={"message": "Not found"})
        if "did:" not in did:
            raise ValidationException(status_code=400, content={"message": "Invalid DID"})

        endpoint = f"{settings.VERIFIER_ENDPOINT}/resolver/resolve/{did}"
        r = requests.get(endpoint)
        try:
            return r.json()["did_document"]
        except:
            raise ValidationException(
                status_code=r.status_code, content={"message": r.text}
            )

    async def fetch_did_document(self):
        verkey = await AskarController(self.did_label).fetch('verkey')
        service_endpoint = f'{settings.HTTPS_BASE}/{settings.DID_NAMESPACE}/{self.did_label}'
        return {
            '@context': [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/v2",
                "https://w3id.org/traceability/v1"
            ],
            'id': self.did,
            'verificationMethod': [{
                'id': f'{self.did}#verkey',
                'type': 'Ed25519VerificationKey2018',
                'controller': self.did,
                'publicKeyBase58': verkey
            }],
            'authentication': [ f'{self.did}#verkey'],
            'assertionMethod': [ f'{self.did}#verkey'],
            'service': [{
                'id': f'{self.did}#traceability-api',
                'type': ["TraceabilityAPI"],
                'serviceEndpoint': service_endpoint
            }]
        }

    async def sign_json_ld(self, credential):
        options = {
            'type': 'Ed25519Signature2018',
            'proofPurpose': 'AssertionMethod',
            'verificationMethod': f'{self.did}#verkey'
        }
        verkey = await AskarController(self.did_label).fetch('verkey')
        body = {"doc": {"credential": credential, "options": options}, "verkey": verkey}
        endpoint = f"{self.endpoint}/jsonld/sign"
        r = requests.post(endpoint, headers=self.headers, json=body)
        try:
            return r.json()["signed_doc"]
        except:
            raise ValidationException(
                status_code=r.status_code, content={"message": r.text}
            )

    def issue_credential(self, credential, options):
        endpoint = f"{self.endpoint}/vc/credentials/issue"
        body = {"credential": credential, "options": options}
        r = requests.post(endpoint, headers=self.headers, json=body)
        try:
            return r.json()["vc"]
        except:
            raise ValidationException(
                status_code=r.status_code, content={"message": r.text}
            )


    def verify_credential(self, vc):
        endpoint = f"{settings.VERIFIER_ENDPOINT}/vc/credentials/verify"
        body = {"verifiableCredential": vc, "options": {}}
        r = requests.post(endpoint, json=body)
        try:
            verifications = r.json()
        except:
            raise ValidationException(
                status_code=r.status_code, content={"message": r.text}
            )
            
        verifications['checks'] = ['proof']
        verifications['errors'] = [verifications['errors']] if 'errors' in verifications else []
        
        if "credentialStatus" in vc:
            if self.get_credential_status(vc):
                verifications['errors'].append('status')
            verifications['checks'].append('status')
            
        issuance_date = datetime.fromisoformat(vc["issuanceDate"])
        if issuance_date < datetime.now(issuance_date.tzinfo):
            verifications['errors'].append('issuanceDate')
        verifications['checks'].append('issuanceDate')
        
        if "expirationDate" in vc:
            expiration_date = datetime.fromisoformat(vc["expirationDate"])
            if expiration_date < datetime.now(expiration_date.tzinfo):
                verifications['errors'].append('expirationDate')
            verifications['checks'].append('expirationDate')
            
        verifications['verified'] = True if len(verifications['errors']) == 0 else False
            
        return verifications

    def verify_presentation(self, vp):
        body = {"verifiablePresentation": vp, "options": {}}
        endpoint = f"{settings.VERIFIER_ENDPOINT}/vc/presentations/verify"
        r = requests.post(endpoint, json=body)
        try:
            return r.json()
        except:
            raise ValidationException(
                status_code=r.status_code, content={"message": r.text}
            )
