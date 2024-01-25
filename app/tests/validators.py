import re


from typing import Union, List, Dict, Optional, Field
from pydantic import BaseModel, validator


def valid_xml_timestamp(timestamp):
    iso8601_regex = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
    match_iso8601 = re.compile(iso8601_regex).match
    try:
        if match_iso8601(timestamp) is None:
            return False
    except:
        pass
    return True


class ValidationException(Exception):
    def __init__(self, content: dict, status_code: int):
        self.content = content
        self.status_code = status_code

class Credential(BaseModel):
    context: List[str] = Field(alias='@context')
    type: List[str]
    id: Optional[str]
    issuer: Union(Dict[str, str], str)
    issuanceDate: str
    credentialStatus: Dict[str, Union(dict, str)]
    credentialSubject: Dict[str, Union(dict, str)]
    

    @validator("context")
    @classmethod
    def validate_context(cls, value):
        if not isinstance(value, list):
            raise ValidationException(
                status_code=400, content={"message": "context must be an array"}
            )
        if not all(isinstance(item, str) for item in value):
            raise ValidationException(
                status_code=400, content={"message": "context items must be strings"}
            )
        return value
    

    @validator("type")
    @classmethod
    def validate_type(cls, value):
        if not isinstance(value, list):
            raise ValidationException(
                status_code=400, content={"message": "credential.type must be an array"}
        )
        if len(value) == 0:
            raise ValidationException(
                status_code=400,
                content={"message": "credential.type must have at least 1 type"},
            )
        if not all(isinstance(item, str) for item in value):
            raise ValidationException(
                status_code=400,
                content={"message": "credential.type items must be strings"},
            )
        return value
    

    @validator("issuer")
    @classmethod
    def validate_issuer(cls, value):
        if not isinstance(value, str) and not isinstance(
            value, dict
        ):
            raise ValidationException(
                status_code=400,
                content={"message": "credential.issuer field must be a string or a dict"},
            )

        if isinstance(value, dict):
            if "id" not in value:
                raise ValidationException(
                    status_code=400, content={"message": "Missing credential.issuer.id"}
                )
            if not isinstance(value["id"], str):
                raise ValidationException(
                    status_code=400,
                    content={"message": "credential.issuer.id must be a string"},
                )

        issuer = (
            value
            if isinstance(value, str)
            else value["id"]
        )
        if "urn:uuid:" in issuer:
            raise ValidationException(
                status_code=422,
                content={"message": f"{issuer} not found"},
            )
        if "did:" not in issuer:
            raise ValidationException(
                status_code=400, content={"message": "Invalid issuer"}
            )
        return value
    

    @validator("issuanceDate")
    @classmethod
    def validate_issuance_date(cls, value):
        if not isinstance(value, str):
            raise ValidationException(
                status_code=400, content={"message": "issuanceDate field must be a string"}
            )

        if not valid_xml_timestamp(value):
            raise ValidationException(
                status_code=400,
                content={"message": "issuanceDate not a xml date time string"},
            )
        return value
    

    @validator("credentialSubject")
    @classmethod
    def validate_credential_subject(cls, value):
        if not isinstance(value, dict):
            raise ValidationException(
                status_code=400,
                content={"message": "credentialSubject field must be an object"},
            )
        if "id" in value:
            if not isinstance(value["id"], str):
                raise ValidationException(
                    status_code=400,
                    content={"message": "credentialSubject.id item must be a string"},
                )
        return value


class VerifiableCredential(BaseModel):
    proof: dict


class Presentation(BaseModel):
    context: list
    type: list
    holder: Union(list, str)


class VerifiablePresentation(BaseModel):
    proof: dict


class Proof(BaseModel):
    type: str
    verificationMethod: str
    

    @validator("type")
    @classmethod
    def validate_type(cls, value):
        if not isinstance(value, str):
            raise ValidationException(
                status_code=400, content={"message": "proof.type field must be a string"}
            )
        if value.isspace() or " " in value:
            raise ValidationException(
                status_code=400,
                content={"message": "proof.type must be a valid proof type"},
            )
        return value
    

    @validator("created")
    @classmethod
    def validate_creation_date(cls, value):
        if not isinstance(value, str):
            raise ValidationException(
                status_code=400, content={"message": "proof.created must be a string"}
            )
        if not valid_xml_timestamp(value):
            raise ValidationException(
                status_code=400,
                content={"message": "proof.created not a xml date time string"},
            )
        return value
    

    @validator("verificationMethod")
    @classmethod
    def validate_verification_method(cls, value):
        if not isinstance(value, str):
            raise ValidationException(
                status_code=400,
                content={"message": "proof.verificationMethod field must be a string"},
            )
        return value
    

    @validator("jws")
    @classmethod
    def validate_jws(cls, value):
        if not isinstance(value, str):
            raise ValidationException(
                status_code=400, content={"message": "jws proof must be a string"}
            )
        return value
    

    @validator("proofPurpose")
    @classmethod
    def validate_proof_purpose(cls, value):
        if not isinstance(value, str):
            raise ValidationException(
                status_code=400,
                content={"message": "proof.proofPurpose field must be a string"},
            )
        return value