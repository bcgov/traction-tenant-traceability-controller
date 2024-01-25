from typing import Union, List
from pydantic import BaseModel, Field
import json


class Service(BaseModel):
    id: str
    type: Union[str, List[str]]
    endpoint: str


class VerificationMethod(BaseModel):
    id: str
    type: Union[str, List[str]]
    controller: str
    publicKeyBase58: str


class DidDocument(BaseModel):
    context: List[str] = Field(alias='@context', default=["https://www.w3.org/ns/did/v1"])
    id: str = Field()
    service: List[Service] = Field(default=[])
    authentication: Union[List[str], List[VerificationMethod]] = Field(default=[])
    assertionMethod: Union[List[str], List[VerificationMethod]] = Field(default=[])
    verificationMethod: List[VerificationMethod] = Field(default=[])

    def add_verkey(self, verkey):
        self.context.append('https://w3id.org/security/v2')
        self.verificationMethod.append(
            {
                "id": f"{self.id}#verkey",
                "type": "Ed25519VerificationKey2018",
                "controller": self.id,
                "publicKeyBase58": verkey,
            })
        self.authentication.append(f"{self.id}#verkey")
        self.assertionMethod.append(f"{self.id}#verkey")

    def add_service(self, service):
        if service == 'TraceabilityAPI':
            # self.context.append("https://w3id.org/traceability/v1")
            endpoint = self.id.replace("did:web:", "").replace(":", "/")
            self.service.append(
                {
                    "id": f"{self.id}#traceability-api",
                    "type": "TraceabilityAPI",
                    "serviceEndpoint": f"https://{endpoint}",
                }
            )
    def as_json(self):
        return json.dumps(dict(self), indent=4)
