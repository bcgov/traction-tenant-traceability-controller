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
    id: str = Field()
    context: List[str] = Field(
        alias="@context", default=["https://www.w3.org/ns/did/v1"]
    )
    service: List[Service] = []
    authentication: Union[List[str], List[VerificationMethod]] = []
    assertionMethod: Union[List[str], List[VerificationMethod]] = []
    verificationMethod: List[VerificationMethod] = []

    def add_verkey(self, verkey):
        self.context.append("https://w3id.org/security/v2")
        self.authentication.append(f"{self.id}#verkey")
        self.assertionMethod.append(f"{self.id}#verkey")
        self.verificationMethod += [
            {
                "id": f"{self.id}#verkey",
                "type": "Ed25519VerificationKey2018",
                "controller": self.id,
                "publicKeyBase58": verkey,
            }
        ]

    def add_service(self, service):
        if service == "TraceabilityAPI":
            # Traceability context bug
            # self.context.append("https://w3id.org/traceability/v1")
            endpoint = self.id.replace("did:web:", "").replace(":", "/")
            self.service.append(
                {
                    "id": f"{self.id}#traceability-api",
                    # TODO, should be a list
                    "type": "TraceabilityAPI",
                    "serviceEndpoint": f"https://{endpoint}",
                }
            )

    def as_json(self):
        return json.dumps(dict(self), indent=2)
