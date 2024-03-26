from typing import Union, List, Dict
from pydantic import BaseModel, Field, AliasChoices, field_validator
from app.validations import (
    ValidationException,
    valid_xml_timestamp,
    valid_credential_subject,
    valid_issuer,
    valid_type,
    valid_context_v1,
    valid_status_update_value,
    valid_status_purpose
)
from .proofs import Proof


class Credential(BaseModel):
    id: str = Field(None)
    type: List[str] = Field()
    issuer: Union[Dict[str, str], str] = Field()
    context: List[str] = Field(alias="@context")
    issuance_date: str = Field(alias="issuanceDate")
    expiration_date: str = Field(None, alias="expirationDate")
    credential_status: dict = Field(None, alias="credentialStatus")
    credential_subject: dict = Field(alias="credentialSubject")

    @field_validator("context")
    @classmethod
    def validate_context(cls, value):
        valid_context_v1(value)
        return value

    @field_validator("type")
    @classmethod
    def validate_credential_type(cls, value):
        valid_type(value)
        if value[0] != "VerifiableCredential":
            raise ValueError("First value must be VerifiableCredential")
        return value

    @field_validator("issuer")
    @classmethod
    def validate_issuer(cls, value):
        valid_issuer(value)
        return value

    @field_validator("issuance_date")
    @classmethod
    def validate_issuance_date(cls, value):
        valid_xml_timestamp(value)
        return value

    @field_validator("expiration_date")
    @classmethod
    def validate_expiration_date(cls, value):
        valid_xml_timestamp(value)
        return value

    @field_validator("credential_subject")
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
    def validate_vc_type(cls, value):
        valid_type(value)
        if value[0] != "VerifiableCredential":
            raise ValueError("First value must be VerifiableCredential")
        return value

    @field_validator("issuer")
    @classmethod
    def validate_issuer(cls, value):
        valid_issuer(value)
        return value

    @field_validator("issuance_date")
    @classmethod
    def validate_issuance_date(cls, value):
        valid_xml_timestamp(value)
        return value

    @field_validator("expiration_date")
    @classmethod
    def validate_expiration_date(cls, value):
        valid_xml_timestamp(value)
        return value

    @field_validator("credential_subject")
    @classmethod
    def validate_credential_subject(cls, value):
        valid_credential_subject(value)
        return value


class CredentialStatusOption(BaseModel):
    type: str = Field()

    @field_validator("type")
    @classmethod
    def validate_status_option_type(cls, value):
        valid_type(value)
        return value


class IssuanceOptions(BaseModel):
    type: str = Field(validation_alias=AliasChoices("proofType", "type"))
    created: str = Field(None)
    domain: str = Field(None)
    challenge: str = Field(None)
    credential_status: CredentialStatusOption = Field(None, alias="credentialStatus")

    @field_validator("type")
    @classmethod
    def validate_signature_type(cls, value):
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
    status_purpose: str = Field(alias="statusPurpose")

    @field_validator("type")
    @classmethod
    def validate_status_entry_type(cls, value):
        valid_type(value)
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        valid_status_update_value(value)
        return value

    @field_validator("status_purpose")
    @classmethod
    def validate_status_purpose(cls, value):
        valid_status_purpose(value)
        return value
