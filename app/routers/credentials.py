from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from config import settings
from datetime import datetime
from app.validations import ValidationException
from app.controllers import agent, status_list, askar, auth, did_web
from app.models.web_requests import (
    IssueCredentialSchema,
    UpdateCredentialStatusSchema,
    VerifyCredentialSchema,
    CredentialVerificationResponse,
)
from app.auth.bearer import JWTBearer
import uuid

router = APIRouter()


@router.get(
    "/{did_label}/credentials/{credentialId}",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Get a verifiable credential by id. Required to make revocable credentials.",
)
async def get_credential(did_label: str, credentialId: str, request: Request):
    await auth.is_authorized(did_label, request)
    return await askar.get_credential(did_label, credentialId)


@router.post(
    "/{did_label}/credentials/issue",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Issue a credential",
)
async def issue_credential(
    did_label: str, request: Request, requestBody: IssueCredentialSchema
):
    await auth.is_authorized(did_label, request)

    requestBody = requestBody.model_dump(by_alias=True, exclude_none=True)
    credential = requestBody["credential"]
    options = requestBody["options"]

    # Ensure the issuer field in the credential has the right value
    did_web.can_issue(credential, did_label)
    did = did_web.from_org_id(did_label)

    # Generate a credential id if none is provided
    if "id" not in credential:
        credential["id"] = f"urn:uuid:{str(uuid.uuid4())}"
    # Fill status information
    if "credentialStatus" in options:
        status = options.pop("credentialStatus")
        credential = await status_list.add_credential_status(did_label, credential, status)

    # Default to #verkey as id
    options["verificationMethod"] = f"{did}#verkey"

    # Backwards compatibility with old json-ld routes in traction,
    # doesn't support created option and requires proofPurpose
    if "created" in options:
        options.pop("created")
    options["proofPurpose"] = "assertionMethod"
    verkey = agent.get_verkey(did)
    vc = agent.sign_json_ld(credential, options, verkey)

    # New vc-api routes
    # vc = agent.issue_credential(credential, options)

    credentialId = credential["id"]
    dataKey = askar.issuedCredentialDataKey(did_label, credentialId)
    await askar.store_data(settings.ASKAR_KEY, dataKey, vc)

    return JSONResponse(status_code=201, content={"verifiableCredential": vc})


@router.post(
    "/{did_label}/credentials/verify",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Verify a credential",
)
async def verify_credential(
    did_label: str, request: Request, requestBody: VerifyCredentialSchema
):
    await auth.is_authorized(did_label, request)

    requestBody = requestBody.dict(exclude_none=True)
    vc = requestBody["verifiableCredential"]
    vc["@context"] = vc.pop("context")
    verification = CredentialVerificationResponse()
    verification = verification.dict()
    verified = agent.verify_credential(vc)
    verification["checks"].append("proof")
    if "errors" in verified:
        verification["errors"] += verified["errors"]

    # Check credential status
    if "credentialStatus" in vc:
        verification["checks"].append("status")
        # vc['credentialStatus']['purpose']
        statusType = vc["credentialStatus"]["type"]
        verification["checks"] += ["status"]
        status = status_list.get_credential_status(vc, statusType)
        if status:
            verification["errors"] += ["revoked"]
            verification["verifications"] = [{"title": "Revocation", "status": "bad"}]

    # Check expiration date
    if "expirationDate" in vc:
        verification["checks"].append("expiration")
        expirationDate = datetime.fromisoformat(vc["expirationDate"])
        timezone = expirationDate.tzinfo
        time_now = datetime.now(timezone)
        if expirationDate < time_now:
            verification["errors"].append("expired")

    if len(verification["errors"]) == 0:
        verification["verified"] = True
    return JSONResponse(status_code=200, content=verification)


@router.post(
    "/{did_label}/credentials/status",
    tags=["Credentials"],
    dependencies=[Depends(JWTBearer())],
    summary="Updates the status of an issued credential.",
)
async def update_credential_status(
    did_label: str, request: Request, requestBody: UpdateCredentialStatusSchema
):
    await auth.is_authorized(did_label, request)
    requestBody = requestBody.dict(exclude_none=True)
    credentialId = requestBody["credentialId"]
    credentialStatus = requestBody["credentialStatus"]

    # We find which status bit to update
    statusBit = credentialStatus[0]["status"]
    statusType = credentialStatus[0]["type"]
    if (
        credentialStatus[0]["type"] in ["StatusList2021Entry"]
        and "statusPurpose" not in credentialStatus[0]
    ):
        raise ValidationException(
            status_code=400, content={"message": "Missing purpose"}
        )

    # We fetch the issued credential based on the credential ID
    dataKey = askar.issuedCredentialDataKey(did_label, credentialId)
    vc = await askar.fetch_data(settings.ASKAR_KEY, dataKey)

    # Make sure the payload refers to the correct status list type
    if vc["credentialStatus"]["type"] != statusType:
        return ValidationException(
            status_code=400,
            content={"message": f"Status list type mismatch"},
        )
    if statusType == "RevocationList2020Status":
        statusCredentialId = statusListType = "RevocationList2020"
        statusCredential = await status_list.change_credential_status(
            vc, statusBit, did_label, statusListType
        )
    elif statusType == "StatusList2021Entry":
        statusCredentialId = statusListType = "StatusList2021"
        statusCredential = await status_list.change_credential_status(
            vc, statusBit, did_label, statusListType
        )

    # Store the new credential
    dataKey = askar.statusCredentialDataKey(did_label, statusCredentialId)
    await askar.update_data(settings.ASKAR_KEY, dataKey, statusCredential)

    return JSONResponse(status_code=200, content={"message": "Status updated"})


@router.get(
    "/{did_label}/credentials/status/{statusCredentialId}",
    tags=["Credentials"],
    summary="Returns a status list credential",
)
async def get_status_list_credential(did_label: str, statusCredentialId: str):
    return await status_list.get_status_list_credential(did_label, statusCredentialId)
