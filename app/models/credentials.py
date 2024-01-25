from typing import Union, List, Dict
from pydantic import BaseModel, Field, field_validator
from .validations import valid_xml_timestamp
import validators

class Credential(BaseModel):
    id: str = Field(None)
    type: List[str] = Field()
    issuer: Union[Dict[str, str], str] = Field()
    context: List[str] = Field(alias="@context")
    issuanceDate: str = Field()
    expirationDate: str = Field(None)
    credentialStatus: dict = Field(None)
    credentialSubject: dict = Field()
    
    @field_validator('context')
    @classmethod
    def validate_context(cls, value):
        if len(value) < 1:
            raise ValueError('Must have items')
        if value[0] != "https://www.w3.org/2018/credentials/v1":
            raise ValueError('First value must be https://www.w3.org/2018/credentials/v1')
        if not all(validators.url(item) for item in value):
            raise ValueError('items must be urls')
        return value
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, value):
        if len(value) < 1:
            raise ValueError('Must have items')
        if value[0] != "VerifiableCredential":
            raise ValueError('First value must be VerifiableCredential')
        return value
    
    @field_validator('issuer')
    @classmethod
    def validate_issuer(cls, value):
        if isinstance(value, dict):
            if "id" not in value:
                raise ValueError('Missing id')
            if not isinstance(value["id"], str):
                raise ValueError('Id must be a string')
        issuer = (
            value
            if isinstance(value, str)
            else value["id"]
        )
        if "urn:uuid:" in issuer:
            raise ValueError('Unknown issuer')
        if "did:" not in issuer:
            raise ValueError('Invalid issuer')
        return value
    
    @field_validator('issuanceDate')
    @classmethod
    def validate_issuance_date(cls, value):
        if not valid_xml_timestamp(value):
            raise ValueError('Not a valid date format')
        return value
    
    @field_validator('expirationDate')
    @classmethod
    def validate_expiration_date(cls, value):
        if not valid_xml_timestamp(value):
            raise ValueError('Not a valid date format')
        return value
    
    @field_validator('credentialSubject')
    @classmethod
    def validate_credential_subject(cls, value):
        if 'id' in value and not isinstance(value['id'], str):
            raise ValueError('Invalid subject id')
        return value


class CredentialStatusOption(BaseModel):
    type: str = Field()

class IssuanceOptions(BaseModel):
    type: str = Field()
    credentialStatus: CredentialStatusOption = Field(None)
    created: str = Field(None)

    @field_validator('type')
    @classmethod
    def validate_type(cls, value):
        if ' ' in value:
            raise ValueError('Invalid type')
        return value


    @field_validator('created')
    @classmethod
    def validate_created(cls, value):
        if not valid_xml_timestamp(value):
            raise ValueError('Not a valid date format')
        return value

class Proof(BaseModel):
    jws: str = Field(None)
    type: str = Field()
    created: str = Field()
    verificationMethod: str = Field()
    proofPurpose: str = Field()

class VerifiableCredential(Credential):
    proof: Proof

class CredentialStatusUpdateItem(BaseModel):
    type: str = Field()
    status: str = Field()
    statusPurpose: str = Field()