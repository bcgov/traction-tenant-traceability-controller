import json
from aries_askar import Store, error
from config import settings
import time
from app.validations import ValidationException
from app.utils import did_from_label
from app.controllers.askar import AskarController



class DidDocumentController:
    
    def __init__(self, did_label):
        self.did_label = did_label
        self.id = did_from_label(did_label)
        self.context = [
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/v2",
            "https://w3id.org/traceability/v1"
        ]
        self.verification_method = []
        self.authentication = []
        self.assertion_method = []
        service = {
            'id': f'{self.id}#traceability-api',
            'type': ["TraceabilityAPI"],
            'serviceEndpoint': f'{settings.HTTPS_BASE}/{settings.DID_NAMESPACE}/{did_label}'
        }
        self.service = [service]
    
    async def add_verkey(self):
        verification_method = {
            'id': f'{self.id}#verkey',
            'type': 'Ed25519VerificationKey2018',
            'controller': self.id,
            'publicKeyBase58': await AskarController(self.did_label).fetch('verkey')
        }
        self.verification_method = [verification_method]
        self.authentication = [verification_method['id']]
        self.assertion_method = [verification_method['id']]
    
    def as_json(self):
        return {
            '@context': self.context,
            'id': self.id,
            'verificationMethod': self.verification_method,
            'authentication': self.authentication,
            'assertionMethod': self.assertion_method,
            'service': self.service,
        }