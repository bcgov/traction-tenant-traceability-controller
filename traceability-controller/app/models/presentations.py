from typing import Union, List, Dict
from pydantic import BaseModel, Field, AliasChoices, field_validator
from app.validations import (
    valid_xml_timestamp,
    valid_credential_subject,
    valid_issuer,
    valid_type,
    valid_context_v1,
)
from .proofs import Proof
from .credentials import VerifiableCredential


class Presentation(BaseModel):
    id: str = Field(None)
    type: List[str] = Field()
    holder: Union[Dict[str, str], str] = Field(None)
    context: List[str] = Field(alias="@context")
    verifiableCredential: List[VerifiableCredential] = Field(None)


class VerifiablePresentation(Presentation):
    proof: Proof = Field()


class SignOptions(BaseModel):
    type: str = Field(validation_alias=AliasChoices("proofType", "type"))
    created: str = Field(None)
    domain: str = Field(None)
    challenge: str = Field(None)
    proofPurpose: str = Field(default="assertionMethod")
    verificationMethod: str = Field(None)

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        valid_type(value)

    @field_validator("created")
    @classmethod
    def validate_created(cls, value):
        valid_xml_timestamp(value)
