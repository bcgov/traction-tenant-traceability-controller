from fastapi import APIRouter, Depends, Response, Header
from typing import Annotated
from config import settings
from app.controllers import agent, redis
from app.models import CreatePresentationInput
from app.auth.bearer import JWTBearer

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
async def create_presentation(
    label: str,
):
    return ""


@router.post(
    "/organization/{label}/presentations/verify",
    tags=["Presentations"],
    dependencies=[Depends(JWTBearer())],
    summary="Verify a presentation",
)
async def verify_presentation(
    label: str,
):
    return ""


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
