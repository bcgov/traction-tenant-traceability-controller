from .credentials import Credential, IssuanceOptions, CredentialStatusUpdateItem, VerifiableCredential
from typing import List
from pydantic import BaseModel, Field, field_validator
import re

CHECK_RE = re.compile('[a-zA-Z0-9_-]+$')

class CreateDIDWebInput(BaseModel):
    label: str = Field(example='')
    
    @field_validator('label')
    @classmethod
    def validate_issuer(cls, value):
        if not CHECK_RE.match(value):
            raise ValueError('must match regex [a-zA-Z0-9_-]+$')
        return value

class IssueCredentialSchema(BaseModel):
    credential: Credential
    options: IssuanceOptions

class VerifyCredentialSchema(BaseModel):
    verifiableCredential: VerifiableCredential

class UpdateCredentialStatusSchema(BaseModel):
    credentialId: str = Field()
    credentialStatus: List[CredentialStatusUpdateItem] = Field()

# class RecievePresentationSchema(BaseModel):
#     credential: Credential
#     options: IssuanceOptions
