from typing import Union, List
from pydantic import BaseModel, Field
from config import settings
import json


class Service(BaseModel):
    id: str
    type: Union[str, List[str]]
    serviceEndpoint: str


class VerificationMethod(BaseModel):
    id: str
    type: Union[str, List[str]]
    controller: str
    publicKeyBase58: str


class DidDocument(BaseModel):
    id: str = Field()
    context: List[str] = Field(
        alias="@context", default=[
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/v2",
            "https://w3id.org/traceability/v1"
        ]
    )
    service: List[Service] = Field(default=[])
    authentication: List[Union[str, VerificationMethod]] = Field(default=[])
    assertionMethod: List[Union[str, VerificationMethod]] = Field(default=[])
    verificationMethod: List[VerificationMethod] = Field(default=[])

    def add_verkey(self, verkey):
        verification_method = VerificationMethod(
            id=f"{self.id}#verkey",
            type="Ed25519VerificationKey2018",
            controller=self.id,
            publicKeyBase58=verkey,
        )
        self.verificationMethod.append(verification_method)
        self.authentication.append(f"{self.id}#verkey")
        self.assertionMethod.append(f"{self.id}#verkey")

    def add_service(self):
        service = Service(
            id=f"{self.id}#traceability-api",
            type=["TraceabilityAPI"],
            serviceEndpoint=f"{settings.HTTPS_BASE}/{settings.DID_NAMESPACE}/{self.id.split(':')[-1]}",
        )
        self.service.append(service)
