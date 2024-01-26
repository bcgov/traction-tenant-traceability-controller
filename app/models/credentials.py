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


class Credential(BaseModel):
    id: str = Field(None)
    type: List[str] = Field()
    issuer: Union[Dict[str, str], str] = Field()
    context: List[str] = Field(alias="@context")
    issuanceDate: str = Field()
    expirationDate: str = Field(None)
    credentialStatus: dict = Field(None)
    credentialSubject: dict = Field()

    @field_validator("context")
    @classmethod
    def validate_context(cls, value):
        valid_context_v1(value)
        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        valid_type(value)
        if value[0] != "VerifiableCredential":
            raise ValueError("First value must be VerifiableCredential")
        return value

    @field_validator("issuer")
    @classmethod
    def validate_issuer(cls, value):
        valid_issuer(value)
        return value

    @field_validator("issuanceDate")
    @classmethod
    def validate_issuance_date(cls, value):
        valid_xml_timestamp(value)
        return value

    @field_validator("expirationDate")
    @classmethod
    def validate_expiration_date(cls, value):
        valid_xml_timestamp(value)
        return value

    @field_validator("credentialSubject")
    @classmethod
    def validate_credential_subject(cls, value):
        valid_credential_subject(value)
        return value


class VerifiableCredential(Credential):
    proof: Proof = Field()

    @field_validator("context")
    @classmethod
    def validate_context(cls, value):
        valid_context_v1(value)
        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        valid_type(value)
        if value[0] != "VerifiableCredential":
            raise ValueError("First value must be VerifiableCredential")
        return value

    @field_validator("issuer")
    @classmethod
    def validate_issuer(cls, value):
        valid_issuer(value)
        return value

    @field_validator("issuanceDate")
    @classmethod
    def validate_issuance_date(cls, value):
        valid_xml_timestamp(value)
        return value

    @field_validator("expirationDate")
    @classmethod
    def validate_expiration_date(cls, value):
        valid_xml_timestamp(value)
        return value

    @field_validator("credentialSubject")
    @classmethod
    def validate_credential_subject(cls, value):
        valid_credential_subject(value)
        return value


class CredentialStatusOption(BaseModel):
    type: str = Field()


class IssuanceOptions(BaseModel):
    type: str = Field(validation_alias=AliasChoices("proofType", "type"))
    created: str = Field(None)
    domain: str = Field(None)
    challenge: str = Field(None)
    credentialStatus: CredentialStatusOption = Field(None)

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        valid_type(value)
        return value

    @field_validator("created")
    @classmethod
    def validate_created(cls, value):
        valid_xml_timestamp(value)
        return value


class CredentialStatusUpdateItem(BaseModel):
    type: str = Field()
    status: str = Field()
    statusPurpose: str = Field(None)
