from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from config import settings
from app.validations import ValidationException
from app.controllers import agent, redis, status_list
from app import validations
from app.auth.bearer import JWTBearer
import uuid
from urllib import parse

router = APIRouter()


@router.get(
    "/organization/{label}/credentials/{credential_id}",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Get a verifiable credential by id. Required to make revocable credentials.",
)
async def get_credential(label: str, credential_id: str, request: Request):
    token = request.headers.get("Authorization")
    agent.verify_token(token)
    label = parse.quote(label.strip().lower())
    try:
        credential = redis.get_credential(label, credential_id)
    except:
        raise ValidationException(
            status_code=404,
            content={"message": f"credential {credential_id} not found"},
        )
    return credential


@router.post(
    "/organization/{label}/credentials/issue",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Issue a credential",
)
async def issue_credential(label: str, request: Request):
    token = request.headers.get("Authorization")
    agent.verify_token(token)
    label = parse.quote(label.strip().lower())

    request = await request.json()
    validations.credentials_issue(request)

    credential = request["credential"]
    options = request["options"]

    # Derive verification from issuer field
    did = (
        credential["issuer"]
        if isinstance(credential["issuer"], str)
        else credential["issuer"]["id"]
    )

    # With the current method of registering did:web in aca-py (leveraging sov keys)
    # we are limited to 1 verification_key per did
    # It's id is #verkey for the timebeing
    options["verificationMethod"] = f"{did}#verkey"

    # Generate a credential id
    if "id" not in credential:
        credential["id"] = f"urn:uuid:{str(uuid.uuid1())}"

    # Fill status information
    if "credentialStatus" in options:
        credential_status = options.pop("credentialStatus")
        status_type = credential_status["type"]
        credential_status = status_list.create_entry(label, status_type)
        credential["credentialStatus"] = credential_status
        if status_type == "RevocationList2020Status":
            credential["@context"].append("https://w3id.org/vc-revocation-list-2020/v1")
        elif status_type == "StatusList2021Entry":
            # original document unavailable https://w3id.org/vc/status-list/v1
            credential["@context"].append(
                "https://raw.githubusercontent.com/digitalbazaar/vc-status-list-context/main/contexts/vc-status-list-v1.jsonld"
            )

    # Backwards compatibility with old json-ld routes in traction,
    # doesn't support created option and requires proofPurpose
    if "created" in options:
        options.pop("created")
    options["proofPurpose"] = "assertionMethod"
    verkey = agent.get_verkey(did, token)
    vc = agent.sign_json_ld(credential, options, verkey, token)

    # New /vc/ldp/issue route
    # Traceability test credentials provide an options.type
    # aca-py needs options.proofType so we have to verify this
    # if "type" in options:
    #     options["proofType"] = options.pop("type")
    # elif "proofType" not in options:
    #     options["proofType"] = "Ed25519Signature2018"
    # vc = agent.issue_credential(credential, options, token)

    redis.store_credential(label, vc)

    return JSONResponse(status_code=201, content={"verifiableCredential": vc})


@router.post(
    "/organization/{label}/credentials/verify",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Verify a credential",
)
async def verify_credential(label: str, request: Request):
    token = request.headers.get("Authorization")
    agent.verify_token(token)
    label = parse.quote(label.strip().lower())

    request = await request.json()
    validations.credentials_verify(request)

    vc = request["verifiableCredential"]

    # Check credential status
    if "credentialStatus" in vc:
        status = status_list.get_credential_status(vc)
        if status:
            # TODO, give proper formatted message
            verified = {
                'verified': False,
                "verifications": {
                    'Revocation': 'bad'
                    }
                }
            
            raise ValidationException(
                status_code=400, content={"message": "Credential is revoked"}
            )
            
    verified = agent.verify_credential(vc, token)

    return JSONResponse(status_code=200, content=verified)


@router.post(
    "/organization/{label}/credentials/status",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Updates the status of an issued credential.",
)
async def update_credential_status(label: str, request: Request):
    token = request.headers.get("Authorization")
    agent.verify_token(token)
    label = parse.quote(label.strip().lower())

    request = await request.json()
    validations.credentials_status(request)

    credential_id = request["credentialId"]
    vc = redis.get_credential(label, credential_id)
    did = vc["issuer"] if isinstance(vc["issuer"], str) else vc["issuer"]["id"]
    verkey = agent.get_verkey(did, token)
    options = {
        "verificationMethod": f"{did}#verkey",
        "proofPurpose": "AssertionMethod",
    }
    for status in request["credentialStatus"]:
        status_type = status["type"]
        status_bit = status["status"]
        status_list_credential = status_list.change_credential_status(
            vc, status_bit, label
        )
        status_list_vc = agent.sign_json_ld(
            status_list_credential, options, verkey, token
        )
        redis.store_status_list(label, status_list_vc)

    return JSONResponse(status_code=200, content={'message': 'Status updated'})


@router.get(
    "/organization/{label}/credentials/status/{status_list_id}",
    tags=["Credentials"],
    summary="Returns a status list credential",
)
async def get_status_list_credential(label: str, status_list_id: str, request: Request):
    label = parse.quote(label.strip().lower())
    status_list_id = f"{settings.HTTPS_BASE}/organization/{label}/credentials/status/{status_list_id}".lower()
    try:
        status_list_vc = redis.get_status_list(label, status_list_id)
    except:
        return ValidationException(
            status_code=404,
            content={"message": f"Status list id {status_list_id} not found"},
        )
    return status_list_vc
