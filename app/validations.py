import re


class ValidationException(Exception):
    def __init__(self, content: dict, status_code: int):
        self.content = content
        self.status_code = status_code


def valid_identifier(issuer):
    # TODO, could be better
    if "urn:uuid:" in issuer:
        raise ValidationException(
            status_code=422,
            content={"message": f"{issuer} not found"},
        )
    if "did:" not in issuer:
        raise ValidationException(
            status_code=400, content={"message": "Invalid issuer"}
        )

    return True


def valid_xml_timestamp(timestamp):
    iso8601_regex = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
    match_iso8601 = re.compile(iso8601_regex).match
    try:
        if match_iso8601(timestamp) is None:
            return False
    except:
        pass
    return True


def valid_type(type):
    if type.isspace():
        return False
    if " " in type:
        return False
    return True


def identifiers_resolve(did):
    # TODO, could be better
    if did[:9] == "urn:uuid:":
        raise ValidationException(status_code=404, content={"message": "Not found"})
    if "did:" not in did:
        raise ValidationException(status_code=400, content={"message": "Invalid DID"})

    return True


def valid_credential(credential):
    # Context
    if not "@context" in credential:
        raise ValidationException(
            status_code=400, content={"message": "Missing context"}
        )
    if not isinstance(credential["@context"], list):
        raise ValidationException(
            status_code=400, content={"message": "context must be an array"}
        )
    if not all(isinstance(item, str) for item in credential["@context"]):
        raise ValidationException(
            status_code=400, content={"message": "context items must be strings"}
        )

    # Credential ID
    if "id" in credential:
        if not isinstance(credential["id"], str):
            raise ValidationException(
                status_code=400, content={"message": "credential.id must be a string"}
            )

    # Credential Type
    if not "type" in credential:
        raise ValidationException(
            status_code=400, content={"message": "Missing credential.type"}
        )
    if not isinstance(credential["type"], list):
        raise ValidationException(
            status_code=400, content={"message": "credential.type must be an array"}
        )
    if len(credential["type"]) == 0:
        raise ValidationException(
            status_code=400,
            content={"message": "credential.type must have at least 1 type"},
        )
    if not all(isinstance(item, str) for item in credential["type"]):
        raise ValidationException(
            status_code=400,
            content={"message": "credential.type items must be strings"},
        )

    # Credential Issuer
    if not "issuer" in credential:
        raise ValidationException(
            status_code=400, content={"message": "Missing credential.issuer"}
        )
    if not isinstance(credential["issuer"], str) and not isinstance(
        credential["issuer"], dict
    ):
        raise ValidationException(
            status_code=400,
            content={"message": "credential.issuer field must be a string or a dict"},
        )

    if isinstance(credential["issuer"], dict):
        if "id" not in credential["issuer"]:
            raise ValidationException(
                status_code=400, content={"message": "Missing credential.issuer.id"}
            )
        if not isinstance(credential["issuer"]["id"], str):
            raise ValidationException(
                status_code=400,
                content={"message": "credential.issuer.id must be a string"},
            )

    issuer = (
        credential["issuer"]
        if isinstance(credential["issuer"], str)
        else credential["issuer"]["id"]
    )
    valid_identifier(issuer)

    # Issuance date
    if not "issuanceDate" in credential:
        raise ValidationException(
            status_code=400, content={"message": "Missing issuanceDate"}
        )
    if not isinstance(credential["issuanceDate"], str):
        raise ValidationException(
            status_code=400, content={"message": "issuanceDate field must be a string"}
        )

    if not valid_xml_timestamp(credential["issuanceDate"]):
        raise ValidationException(
            status_code=400,
            content={"message": "issuanceDate not a xml date time string"},
        )

    # Credential Subject
    if not "credentialSubject" in credential:
        raise ValidationException(
            status_code=400, content={"message": "Missing credentialSubject"}
        )
    if not isinstance(credential["credentialSubject"], dict):
        raise ValidationException(
            status_code=400,
            content={"message": "credentialSubject field must be an object"},
        )
    if "id" in credential["credentialSubject"]:
        if not isinstance(credential["credentialSubject"]["id"], str):
            raise ValidationException(
                status_code=400,
                content={"message": "credentialSubject.id item must be a string"},
            )
    return True


def valid_proof(proof):
    # Proof
    if not isinstance(proof, dict):
        raise ValidationException(
            status_code=400, content={"message": "proof field must be an object"}
        )
    if not "type" in proof:
        raise ValidationException(
            status_code=400, content={"message": "Missing proof.type"}
        )
    if not isinstance(proof["type"], str):
        raise ValidationException(
            status_code=400, content={"message": "proof.type field must be a string"}
        )
    if not valid_type(proof["type"]):
        raise ValidationException(
            status_code=400,
            content={"message": "proof.type must be a valid proof type"},
        )

    if "created" in proof:
        if not isinstance(proof["created"], str):
            raise ValidationException(
                status_code=400, content={"message": "proof.created must be a string"}
            )
        if not valid_xml_timestamp(proof["created"]):
            raise ValidationException(
                status_code=400,
                content={"message": "proof.created not a xml date time string"},
            )

    if "verificationMethod" in proof:
        if not isinstance(proof["verificationMethod"], str):
            raise ValidationException(
                status_code=400,
                content={"message": "proof.verificationMethod field must be a string"},
            )

    if "jws" in proof:
        if not isinstance(proof["jws"], str):
            raise ValidationException(
                status_code=400, content={"message": "jws proof must be a string"}
            )

    if "proofPurpose" in proof:
        if not isinstance(proof["proofPurpose"], str):
            raise ValidationException(
                status_code=400,
                content={"message": "proof.proofPurpose field must be a string"},
            )
    return True


def credentials_issue(request):
    if "credential" not in request:
        raise ValidationException(
            status_code=400, content={"message": "Missing credential"}
        )

    credential = request["credential"]
    if not valid_credential(credential):
        raise ValidationException(
            status_code=400, content={"message": "Invalid credential"}
        )

    # Options
    if "options" not in request:
        raise ValidationException(
            status_code=400, content={"message": "Missing options"}
        )

    options = request["options"]
    if not isinstance(options, dict):
        raise ValidationException(
            status_code=400, content={"message": "Options must be an object"}
        )
    if not "type" in options:
        raise ValidationException(
            status_code=400, content={"message": "Missing options.type field"}
        )
    if not isinstance(options["type"], str):
        raise ValidationException(
            status_code=400, content={"message": "options.type field must be a string"}
        )
    if not valid_type(options["type"]):
        raise ValidationException(
            status_code=400, content={"message": "Invalid options.type"}
        )

    # Missing invalid
    if "created" in options:
        if not isinstance(options["created"], str):
            raise ValidationException(
                status_code=400,
                content={"message": "options.created field must be a string"},
            )
        if not valid_xml_timestamp(options["created"]):
            raise ValidationException(
                status_code=400,
                content={"message": "options.created not a xml date time string"},
            )

    if "credentialStatus" in options:
        if not isinstance(options["credentialStatus"], dict):
            raise ValidationException(
                status_code=400,
                content={"message": "options.credentialStatus field must be an object"},
            )
        if "type" not in options["credentialStatus"]:
            raise ValidationException(
                status_code=400,
                content={"message": "Missing options.credentialStatus.type field"},
            )
        if not isinstance(options["credentialStatus"]["type"], str):
            raise ValidationException(
                status_code=400,
                content={
                    "message": "options.credentialStatus.type field must be a string"
                },
            )
        if not valid_type(options["credentialStatus"]["type"]):
            raise ValidationException(
                status_code=400,
                content={"message": "Invalid options.credentialStatus.type"},
            )

    return True


def credentials_status(request):
    if "credentialId" not in request:
        raise ValidationException(
            status_code=400, content={"message": "Missing credentialId"}
        )
    if not isinstance(request["credentialId"], str):
        raise ValidationException(
            status_code=400, content={"message": "credentialId field must be a string"}
        )
    if "credentialStatus" not in request:
        raise ValidationException(
            status_code=400, content={"message": "Missing credentialStatus"}
        )
    # Bug in traceability test suite, they use the credentialstatus instead of credentialStatus key
    credential_status = (
        request["credentialstatus"]
        if "credentialstatus" in request
        else request["credentialStatus"]
    )
    if not isinstance(credential_status, list):
        raise ValidationException(
            status_code=400,
            content={"message": "credentialStatus field must be a list"},
        )
    if not all(isinstance(item, dict) for item in credential_status):
        raise ValidationException(
            status_code=400,
            content={"message": "credentialStatus.items must be objects"},
        )
    if len(credential_status) > 1:
        raise ValidationException(
            status_code=400,
            content={"message": "credentialStatus can only contain 0 or 1 item"},
        )
    for item in credential_status:
        if "type" not in item:
            raise ValidationException(
                status_code=400,
                content={"message": "credentialStatus.items must have type"},
            )
        if not isinstance(item["type"], str):
            raise ValidationException(
                status_code=400,
                content={"message": "type must be a string"},
            )
        if not valid_type(item["type"]):
            raise ValidationException(
                status_code=400,
                content={"message": "invalid type"},
            )
        if "status" not in item:
            raise ValidationException(
                status_code=400,
                content={"message": "credentialStatus.items must have status"},
            )
        if not isinstance(item["status"], str):
            raise ValidationException(
                status_code=400,
                content={"message": "status must be a string"},
            )
        if item["status"] not in ["0", "1"]:
            raise ValidationException(
                status_code=400,
                content={"message": "status must be 0 or 1"},
            )
        if "statusPurpose" not in item and item["type"] == "StatusList2021Entry":
            raise ValidationException(
                status_code=400,
                content={"message": "StatusList2021Entry must contain statusPurpose"},
            )

        if "statusPurpose" in item and item["type"] == "StatusList2021Entry":
            if not isinstance(item["statusPurpose"], str):
                raise ValidationException(
                    status_code=400,
                    content={"message": "statusPurpose must be a string"},
                )

    return True


def credentials_verify(request):
    if "verifiableCredential" not in request:
        raise ValidationException(
            status_code=400, content={"message": "Missing verifiableCredential"}
        )

    vc = request["verifiableCredential"]
    if not isinstance(vc, dict):
        raise ValidationException(
            status_code=400,
            content={"message": "verifiableCredential must be an object"},
        )
    if not "proof" in vc:
        raise ValidationException(status_code=400, content={"message": "Missing proof"})

    credential = vc
    proof = vc["proof"]
    if not valid_credential(credential):
        raise ValidationException(
            status_code=400, content={"message": "Invalid credential"}
        )
    if not valid_proof(proof):
        raise ValidationException(status_code=400, content={"message": "Invalid proof"})

    return True
