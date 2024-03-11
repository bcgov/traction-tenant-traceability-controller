from fastapi import APIRouter, Depends, Request, Security
from app.models.web_requests import CreateDIDWebInput
from app.validations import valid_did
from app.controllers import auth, agent, status_list, did_web
from config import settings
from app.auth.bearer import JWTBearer
from app.auth.handler import get_api_key
from app.utils import new_issuer_client
import uuid

router = APIRouter()


@router.post("/", tags=["Identifiers"], summary="Create Web DID")
async def register_org_did(
    requestBody: CreateDIDWebInput,
    apiKey: str = Security(get_api_key),
):
    label = vars(requestBody)["label"]

    # Generate uuid if no label was provided
    did_label = label if label else str(uuid.uuid4())

    # Register with traction
    await did_web.register(did_label)
    did = did_web.from_org_id(did_label)

    # Create Status List VCs
    await status_list.create(did_label, "RevocationList2020")
    await status_list.create(did_label, "StatusList2021", purpose="revocation")

    # Generate client credentials and store hash
    clientId, clientSecret = await new_issuer_client(did_label)

    return {
        "did": did,
        "client_id": clientId,
        "client_secret": clientSecret,
        "token_audience": f"{settings.HTTPS_BASE}",
        "token_endpoint": f"{settings.HTTPS_BASE}/oauth/token",
        "service_endpoint": f"{settings.HTTPS_BASE}/{settings.DID_NAMESPACE}/{did_label}",
    }


@router.get(
    "/{did_label}/did.json",
    tags=["Identifiers"],
    summary="Get a DID's latest keys, services and capabilities",
)
async def get_did(did_label: str):
    return await did_web.get_did_document(did_label)


@router.get(
    "/{did_label}/identifiers/{did}",
    tags=["Identifiers"],
    dependencies=[Depends(JWTBearer())],
    summary="Get a DID's latest keys, services and capabilities",
)
async def get_did(did_label: str, did: str, request: Request):
    await auth.is_authorized(did_label, request)
    valid_did(did)
    didDocument = agent.resolve_did(did)

    return {"didDocument": didDocument}
