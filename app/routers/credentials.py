from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from config import settings
from datetime import datetime
from app.validations import ValidationException
from app.controllers import agent, status_list, askar
from app.models.web_requests import (
    IssueCredentialSchema,
    UpdateCredentialStatusSchema,
    VerifyCredentialSchema,
    CredentialVerificationResponse,
)
from app.auth.bearer import JWTBearer
from app.auth.handler import is_authorized
from app.utils import format_label
import uuid

router = APIRouter()


@router.get(
    "/organization/{label}/credentials/{credential_id}",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Get a verifiable credential by id. Required to make revocable credentials.",
)
async def get_credential(label: str, credential_id: str, request: Request):
    label = is_authorized(label, request)
    try:
        data_key = f"{label}:credentials:{credential_id}"
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
async def issue_credential(
    label: str, request: Request, request_body: IssueCredentialSchema
):
    label = is_authorized(label, request)

    request_body = request_body.dict(exclude_none=True)
    credential = request_body["credential"]
    credential["@context"] = credential.pop("context")
    options = request_body["options"]
    # Generate a credential id if none is provided
    if "id" not in credential:
        credential["id"] = f"urn:uuid:{str(uuid.uuid4())}"

    # Fill status information
    if "credentialStatus" in options:
        if options["credentialStatus"]["type"] == "StatusList2021Entry":
            credential["@context"].append("https://w3id.org/vc/status-list/2021/v1")
            credential["credentialStatus"] = await status_list.create_entry(
                label, "StatusList2021"
            )
        elif options["credentialStatus"]["type"] == "RevocationList2020Status":
            credential["@context"].append("https://w3id.org/vc-revocation-list-2020/v1")
            credential["credentialStatus"] = await status_list.create_entry(
                label, "RevocationList2020"
            )
        options.pop("credentialStatus")
    
    issuer_did = (
        credential["issuer"]
        if isinstance(credential["issuer"], str)
        else credential["issuer"]["id"]
    )
    did = f"{settings.DID_WEB_BASE}:organization:{label}"
    if did != issuer_did:
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
async def verify_credential(
    label: str, request: Request, request_body: VerifyCredentialSchema
):
    label = is_authorized(label, request)

    request_body = request_body.dict(exclude_none=True)
    vc = request_body["verifiableCredential"]
    vc["@context"] = vc.pop("context")
    verification = CredentialVerificationResponse()
    verification = verification.dict()
    verified = agent.verify_credential(vc)
    verification['checks'].append('proof')
    if 'errors' in verified:
        verification['errors'] += verified['errors']

    # Check credential status
    if "credentialStatus" in vc:
        verification['checks'].append('status')
        # vc['credentialStatus']['purpose']
        status_type = vc['credentialStatus']['type']
        verification["checks"] += ["status"]
        status = status_list.get_credential_status(vc, status_type)
        if status:
            verification["errors"] += ["revoked"]
            verification["verifications"] = [{"title": "Revocation", "status": "bad"}]

    # Check expiration date
    if "expirationDate" in vc:
        verification["checks"].append("expiration")
        expiration_time = datetime.fromisoformat(vc["expirationDate"])
        timezone = expiration_time.tzinfo
        time_now = datetime.now(timezone)
        if expiration_time < time_now:
            verification["errors"].append("expired")

    if len(verification["errors"]) == 0:
        verification["verified"] = True
    return JSONResponse(status_code=200, content=verification)


@router.post(
    "/organization/{label}/credentials/status",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Updates the status of an issued credential.",
)
async def update_credential_status(
    label: str, request: Request, request_body: UpdateCredentialStatusSchema
):
    label = is_authorized(label, request)
    request_body = request_body.dict(exclude_none=True)
    credential_id = request_body["credentialId"]
    credential_status = request_body["credentialStatus"]
    
    # We find which status bit to update
    status_bit = credential_status[0]["status"]
    status_type = credential_status[0]['type']
    if credential_status[0]['type'] in ['StatusList2021Entry'] and 'statusPurpose' not in credential_status:
        raise ValidationException(status_code=400, content={"message": "Missing purpose"})

    # We fetch the issued credential based on the credential ID
    data_key = f"{label}:credentials:{credential_id}".lower()
    vc = await askar.fetch_data(settings.ASKAR_KEY, data_key)
    
    # Make sure the payload refers to the correct status list type
    if vc['credentialStatus']['type'] != status_type:
        return ValidationException(
            status_code=400,
            content={"message": f"Status list type mismatch"},
        )
    if status_type == 'RevocationList2020Status':
        list_type = 'RevocationList2020'
        new_status_list_vc = await status_list.change_credential_status(
            vc, status_bit, label, list_type
        )
    elif status_type == 'StatusList2021Entry':
        list_type = 'StatusList2021'
        new_status_list_vc = await status_list.change_credential_status(
            vc, status_bit, label, list_type
        )
    
    # Store the new credential
    data_key = f"{label}:status_lists:{list_type}"
    await askar.update_data(settings.ASKAR_KEY, data_key, new_status_list_vc)

    return JSONResponse(status_code=200, content={"message": "Status updated"})


@router.get(
    "/organization/{label}/credentials/status/{list_type}",
    tags=["Credentials"],
    summary="Returns a status list credential",
)
async def get_status_list_credential(label: str, list_type: str):
    label = format_label(label)
    try:
        data_key = f"{label}:status_lists:{list_type}"
        status_list_vc = await askar.fetch_data(settings.ASKAR_KEY, data_key)
    except:
        return ValidationException(
            status_code=404,
            content={"message": "Status list not found"},
        )
    return status_list_vc
