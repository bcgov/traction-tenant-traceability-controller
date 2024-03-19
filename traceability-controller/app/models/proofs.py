from pydantic import BaseModel, Field, AliasChoices, field_validator
from app.validations import (
    valid_xml_timestamp,
    valid_type,
)


class Proof(BaseModel):
    type: str = Field()
    created: str = Field()
    jws: str = Field()
    # proofValue: str = Field(validation_alias=AliasChoices("proofValue", "jws"))
    proofPurpose: str = Field()
    verificationMethod: str = Field()

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
