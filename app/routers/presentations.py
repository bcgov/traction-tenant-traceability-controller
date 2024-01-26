from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from typing import Annotated
from config import settings
from app.validations import ValidationException
from app.controllers import askar, agent
from app.auth.bearer import JWTBearer
from app.auth.handler import is_authorized
from ..utils import format_label

router = APIRouter()


@router.post(
    "/organization/{label}/presentations",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Create a presentation. This endpoint allows clients holding a valid OAuth2 access token to create a presentation.",
)
async def create_presentation_auth(
    label: str,
    request: Request,
    Authorization: Annotated[str | None, Header()] = None,
):
    vp = await request.json()
    
    for vc in vp['verifiableCredential']:
        verified = agent.verify_credential(vc)
    
    return JSONResponse(status_code=200, content={})


@router.post(
    "/organization/{label}/presentations/prove",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Create a presentation",
)
async def sign_presentation(label: str, request: Request):
    label = is_authorized(label, request)

    request = await request.json()

    presentation = request["presentation"]
    options = request["options"]

    holder_did = (
        presentation["holder"]
        if isinstance(presentation["holder"], str)
        else presentation["holder"]["id"]
    )
    did = f"{settings.DID_WEB_BASE}:organization:{label}"
    if did != holder_did:
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
    "/organization/{label}/presentations/verify",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Verify a presentation",
)
async def verify_presentation(label: str, request: Request):
    label = is_authorized(label, request)

    request = await request.json()

    vp = request["verifiablePresentation"]
    verified = agent.verify_presentation(vp)

    return JSONResponse(status_code=200, content=verified)


@router.post(
    "/organization/{label}/presentations/available",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Start a presentation exchange flow",
)
async def start_presentation(
    label: str,
    request: Request,
):
    return ""


@router.post(
    "/organization/{label}/presentations/submissions",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="End a presentation exchange flow",
)
async def end_presentation(
    label: str,
    request: Request,
):
    return ""
