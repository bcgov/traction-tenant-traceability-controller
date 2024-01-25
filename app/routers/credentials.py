from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from config import settings
from app.models.validations import ValidationException
from app.controllers import agent, status_list, askar
from app.models.web_requests import IssueCredentialSchema, UpdateCredentialStatusSchema, VerifyCredentialSchema
from app.auth.bearer import JWTBearer
from app.auth.handler import is_authorized
from ..utils import format_label
import uuid

router = APIRouter()


@router.get(
    "/organization/{label}/credentials/{credential_id}",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Get a verifiable credential by id. Required to make revocable credentials.",
)
async def get_credential(label: str, credential_id: str, request: Request):
    token = request.headers.get("Authorization").replace("Bearer ", "")
    label = format_label(label)
    if not is_authorized(token, label):
        raise ValidationException(
            status_code=401, content={"message": "Unauthorized"}
        )
    try:
        data_key = f"{label}:credentials:{credential_id}".lower()
        credential = await askar.fetch_data(settings.ASKAR_KEY, data_key)
        return credential
    except:
        raise ValidationException(
            status_code=404,
            content={"message": f"credential {credential_id} not found"},
        )


@router.post(
    "/organization/{label}/credentials/issue",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Issue a credential",
)
async def issue_credential(label: str, request: Request, request_body: IssueCredentialSchema):
    token = request.headers.get("Authorization").replace("Bearer ", "")
    label = format_label(label)
    if not is_authorized(token, label):
        raise ValidationException(
            status_code=401, content={"message": "Unauthorized"}
        )
    request_body = request_body.dict(exclude_none=True)
    credential = request_body['credential']
    credential['@context'] = credential.pop('context')
    options = request_body['options']

    # Generate a credential id if none is provided
    if "id" not in credential:
        credential["id"] = f"urn:uuid:{str(uuid.uuid1())}"

    # Fill status information
    if "credentialStatus" in options:
        if options['credentialStatus']['type'] != 'StatusList2021Entry':
            raise ValidationException(
                status_code=400, content={"message": "Credential status type not supported"}
            )
        credential_status = options.pop("credentialStatus")
        credential_status = await status_list.create_entry(label)
        credential["credentialStatus"] = credential_status
        credential["@context"].append("https://w3id.org/vc/status-list/2021/v1")

    # TODO, improve this, we want to validate that the right issuer was used in the credential
    credential_did = (
        credential["issuer"]
        if isinstance(credential["issuer"], str)
        else credential["issuer"]["id"]
    )
    did = f"{settings.DID_WEB_BASE}:organization:{label}"
    if did != credential_did:
        raise ValidationException(
            status_code=400, content={"message": "Invalid issuer"}
        )
    # Limited to 1 verification_key per did and we use #verkey as id
    options["verificationMethod"] = f"{did}#verkey"

    # Backwards compatibility with old json-ld routes in traction,
    # doesn't support created option and requires proofPurpose
    if "created" in options:
        options.pop("created")
    options["proofPurpose"] = "assertionMethod"
    verkey = agent.get_verkey(did)
    vc = agent.sign_json_ld(credential, options, verkey)

    # New vc-api routes
    # vc = agent.issue_credential(credential, options, token)

    data_key = f'{label}:credentials:{credential["id"]}'.lower()
    await askar.store_data(settings.ASKAR_KEY, data_key, credential)

    return JSONResponse(status_code=201, content={"verifiableCredential": vc})


@router.post(
    "/organization/{label}/credentials/verify",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Verify a credential",
)
async def verify_credential(label: str, request: Request, request_body: VerifyCredentialSchema):
    token = request.headers.get("Authorization").replace("Bearer ", "")
    label = format_label(label)
    if not is_authorized(token, label):
        raise ValidationException(
            status_code=401, content={"message": "Unauthorized"}
        )
        
    request_body = request_body.dict(exclude_none=True)
    vc = request_body["verifiableCredential"]
    vc['@context'] = vc.pop('context')
    verification = {
        "verified": None,
        "checks": [],
        "warnings": [],
        "errors": [],
        "verifications": []
    }

    # Check credential status
    if "credentialStatus" in vc:
        # vc['credentialStatus']['purpose']
        verification['checks'].append("STATUS")
        status = status_list.get_credential_status(vc)
        if status:
            verification['errors'].append('revoked')
            verification['warnings'].append('revoked')
            verification['verifications'].append({"title": "Revocation", "status": "bad"})

    # Check expiration date
    if "expirationDate" in vc:
        verification['checks'].append("EXPIRATION")
        expired = False
        if expired:
            verification['errors'].append('expired')
            verification['warnings'].append('expired')

    verified = agent.verify_credential(vc)
    verification['checks'].append("PROOF")
    try:
        if not verified['verified']:
            verification['errors'].append('invalid proof')
            verification['warnings'].append('invalid proof')
        if len(verification['errors']) == 0 and len(verification['warnings']) == 0:
            verification['verified'] = True
        else:
            verification['verified'] = False
        return JSONResponse(status_code=200, content=verification)
    except:
        verification['verified'] = False
        verification['errors'].append('verifier error')
        return JSONResponse(status_code=500, content=verification)
        


@router.post(
    "/organization/{label}/credentials/status",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Updates the status of an issued credential.",
)
async def update_credential_status(label: str, request: Request, request_body: UpdateCredentialStatusSchema):
    token = request.headers.get("Authorization").replace("Bearer ", "")
    label = format_label(label)
    if not is_authorized(token, label):
        raise ValidationException(
            status_code=401, content={"message": "Unauthorized"}
        )
    request_body = request_body.dict(exclude_none=True)
    credential_id = request_body["credentialId"]
    statuses = request_body["credentialStatus"]
    
    data_key = f"{label}:credentials:{credential_id}".lower()
    vc = await askar.fetch_data(settings.ASKAR_KEY, data_key)

    did = vc["issuer"] if isinstance(vc["issuer"], str) else vc["issuer"]["id"]
    verkey = agent.get_verkey(did)
    options = {
        "verificationMethod": f"{did}#verkey",
        "proofPurpose": "AssertionMethod",
    }
    for status in statuses:
        status_bit = status["status"]
        status_list_credential = await status_list.change_credential_status(
            vc, status_bit, label
        )
        status_list_vc = agent.sign_json_ld(
            status_list_credential, options, verkey
        )
        data_key = f'{label}:status_list'
        await askar.update_data(settings.ASKAR_KEY, data_key, status_list_vc)

    return JSONResponse(status_code=200, content={"message": "Status updated"})

@router.get(
    "/organization/{label}/credentials/status/revocation",
    tags=["Credentials"],
    summary="Returns a status list credential",
)
async def get_status_list_credential(label: str):
    label = format_label(label)
    try:
        data_key = f"{label}:status_list"
        status_list_vc = await askar.fetch_data(settings.ASKAR_KEY, data_key)
    except:
        return ValidationException(
            status_code=404,
            content={"message": f"Status list not found"},
        )
    return status_list_vc
