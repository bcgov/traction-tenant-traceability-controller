import re
import validators


class ValidationException(Exception):
    def __init__(self, content: dict, status_code: int):
        self.content = content
        self.status_code = status_code


def valid_xml_timestamp(timestamp):
    iso8601_regex = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
    match_iso8601 = re.compile(iso8601_regex).match
    if match_iso8601(timestamp) is None:
        raise ValueError("Not a valid xml timestamp")


def valid_credential_subject(credential_subject):
    if "id" in credential_subject and not isinstance(credential_subject["id"], str):
        raise ValueError("Invalid subject id")


def valid_status_purpose(status_purpose):
    if not isinstance(status_purpose, str):
        raise ValueError("Invalid status purpose")


def valid_context_v1(context):
    if len(context) < 1:
        raise ValueError("Must have items")
    if not all(validators.url(item) for item in context):
        raise ValueError("items must be urls")
    if context[0] != "https://www.w3.org/2018/credentials/v1":
        raise ValueError("First value must be https://www.w3.org/2018/credentials/v1")


def valid_context_v2(context):
    if len(context) < 1:
        raise ValueError("Must have items")
    if not all(validators.url(item) for item in context):
        raise ValueError("items must be urls")
    if context[0] != "https://www.w3.org/ns/credentials/v2":
        raise ValueError("First value must be https://www.w3.org/ns/credentials/v2")


def valid_type(type):
    if len(type) < 1:
        raise ValueError("Must have items")
    for item in type:
        if " " in item:
            raise ValueError("Invalid type")


def valid_issuer(issuer):
    if isinstance(issuer, dict):
        if "id" not in issuer:
            raise ValueError("Missing id")
        if not isinstance(issuer["id"], str):
            raise ValueError("Id must be a string")
    did = issuer if isinstance(issuer, str) else issuer["id"]
    if "urn:uuid:" in did:
        raise ValueError("Unknown issuer")
    if "did:" not in did:
        raise ValueError("Invalid issuer")


def valid_did(did):
    # TODO, improve did validation
    if did[:9] == "urn:uuid:":
        raise ValidationException(status_code=404, content={"message": "Not found"})
    if "did:" not in did:
        raise ValidationException(status_code=400, content={"message": "Invalid DID"})


def valid_status_update_value(value):
    if value not in ["0", "1"]:
        raise ValidationException(
            status_code=400, content={"message": "Invalid status value"}
        )
