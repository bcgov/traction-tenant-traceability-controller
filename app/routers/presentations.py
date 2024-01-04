from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from typing import Annotated
from config import settings
from app.controllers import agent
from app.auth.bearer import JWTBearer
from app import validations
from urllib import parse

router = APIRouter()


@router.post(
    "/organization/{label}/presentations",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Create a presentation. This endpoint allows clients holding a valid OAuth2 access token to create a presentation.",
)
async def create_presentation_auth(
    label: str,
    Authorization: Annotated[str | None, Header()] = None,
):
    return {}


@router.post(
    "/organization/{label}/presentations/prove",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Create a presentation",
)
async def sign_presentation(label: str, request: Request):
    token = request.headers.get("Authorization")
    agent.verify_token(token)
    label = parse.quote(label.strip().lower())

    request = await request.json()
    # validations.presentations_sign(request)

    presentation = request["presentation"]
    options = request["options"]

    did = (
        presentation["holder"]
        if isinstance(presentation["holder"], str)
        else presentation["holder"]["id"]
    )
    options["verificationMethod"] = f"{did}#verkey"

    # Backwards compatibility with old json-ld routes in traction,
    # doesn't support created option and requires proofPurpose
    if "created" in options:
        options.pop("created")
    options["proofPurpose"] = "assertionMethod"
    verkey = agent.get_verkey(did, token)
    vp = agent.sign_json_ld(presentation, options, verkey, token)

    return JSONResponse(status_code=201, content={"verifiablePresentation": vp})


@router.post(
    "/organization/{label}/presentations/verify",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Verify a presentation",
)
async def verify_presentation(label: str, request: Request):
    token = request.headers.get("Authorization")
    agent.verify_token(token)
    label = parse.quote(label.strip().lower())

    request = await request.json()
    # validations.presentations_verify(request)

    vp = request["verifiablePresentation"]
    verified = agent.verify_presentation(vp, token)

    return JSONResponse(status_code=200, content=verified)


@router.post(
    "/organization/{label}/presentations/available",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Start a presentation exchange flow",
)
async def start_presentation(
    label: str,
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
):
    return ""
