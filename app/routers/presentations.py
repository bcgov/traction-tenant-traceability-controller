from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from typing import Annotated
from config import settings
from app.validations import ValidationException
from app.controllers import askar, agent, auth
from app.auth.bearer import JWTBearer
from app.auth.handler import is_authorized

router = APIRouter()


@router.post(
    "/organizations/{orgId}/presentations",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Create a presentation. This endpoint allows clients holding a valid OAuth2 access token to create a presentation.",
)
async def create_presentation_auth(
    orgId: str,
    request: Request,
    Authorization: Annotated[str | None, Header()] = None,
):
    await auth.is_authorized(orgId, request)
    vp = await request.json()

    for vc in vp["verifiableCredential"]:
        verified = agent.verify_credential(vc)

    return JSONResponse(status_code=200, content={})


@router.post(
    "/organizations/{orgId}/presentations/prove",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Create a presentation",
)
async def sign_presentation(orgId: str, request: Request):
    await auth.is_authorized(orgId, request)

    request = await request.json()

    presentation = request["presentation"]
    options = request["options"]

    holderDid = (
        presentation["holder"]
        if isinstance(presentation["holder"], str)
        else presentation["holder"]["id"]
    )
    did = f"{settings.DID_WEB_BASE}:organization:{orgId}"
    if did != holderDid:
        raise ValidationException(
            status_code=400, content={"message": "Invalid issuer"}
        )
    options["verificationMethod"] = f"{did}#verkey"

    # Backwards compatibility with old json-ld routes in traction,
    # doesn't support created option and requires proofPurpose
    if "created" in options:
        options.pop("created")
    options["proofPurpose"] = "assertionMethod"
    verkey = agent.get_verkey(did)
    vp = agent.sign_json_ld(presentation, options, verkey)

    return JSONResponse(status_code=201, content={"verifiablePresentation": vp})


@router.post(
    "/organizations/{orgId}/presentations/verify",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Verify a presentation",
)
async def verify_presentation(orgId: str, request: Request):
    await auth.is_authorized(orgId, request)

    request = await request.json()

    vp = request["verifiablePresentation"]
    verified = agent.verify_presentation(vp)

    return JSONResponse(status_code=200, content=verified)


@router.post(
    "/organizations/{orgId}/presentations/available",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Start a presentation exchange flow",
)
async def start_presentation(
    orgId: str,
    request: Request,
):
    await auth.is_authorized(orgId, request)
    return ""


@router.post(
    "/organizations/{orgId}/presentations/submissions",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="End a presentation exchange flow",
)
async def end_presentation(
    orgId: str,
    request: Request,
):
    await auth.is_authorized(orgId, request)
    return ""
