from typing import Union, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from config import settings
import json, secrets


class OAuthInput(BaseModel):
    client_id: str = ''
    client_secret: str = ''


class CreateDIDWebInput(BaseModel):
    label: str = 'companyname'


class IssueCredentialInput(BaseModel):
    credential: dict = Field(example={})
    options: dict | None = Field(example={})


class VerifyCredentialInput(BaseModel):
    verifiableCredential: dict = {}


class UpdateCredentialStatusInput(BaseModel):
    credentialId: str = ''
    credentialStatus: dict = {}


class CreatePresentationInput(BaseModel):
    context: list = Field(
        alias="@context",
        example=[
            "https://www.w3.org/2018/credentials/v1",
            "https://w3id.org/traceability/v1",
        ],
    )
    type: list = ["VerifiablePresentation", "TraceablePresentation"]
    verifiableCredential: list = [{}]