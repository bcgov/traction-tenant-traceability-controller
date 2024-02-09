from fastapi import APIRouter, Depends, Request, Security
from app.models.web_requests import CreateDIDWebInput
from app.models.did_document import DidDocument
from app.validations import ValidationException, valid_did
from app.controllers import askar, agent, status_list
from config import settings
from app.auth.bearer import JWTBearer
from app.auth.handler import get_api_key, is_authorized
from app.utils import format_label, did_from_label, new_client

router = APIRouter()


@router.post("/register/did", tags=["Identifiers"], summary="Create Web DID")
async def register(
    request_body: CreateDIDWebInput,
    request: Request,
    api_key: str = Security(get_api_key),
):
    request_body = await request.json()

    # Create a did:web identifier and register with traction
    label = format_label(request_body["label"])
    did = did_from_label(label)
    # TODO, change to web
    verkey = agent.create_did("sov", "ed25519", did)

    # Publish did document
    did_doc = DidDocument(id=did)
    did_doc.add_verkey(verkey)
    did_doc.add_service("TraceabilityAPI")
    did_doc = did_doc.dict()
    did_doc["@context"] = did_doc.pop("context")
    
    data_key = f"{label}:did_document"
    await askar.store_data(settings.ASKAR_KEY, data_key, did_doc)

    # Publish Status List VCs
    status_list_lenght = settings.STATUS_LIST_LENGHT
    for list_type in ["StatusList2021", "RevocationList2020"]:
        status_list_id = (
            f"{settings.HTTPS_BASE}/organization/{label}/credentials/status/{list_type}"
        )
        status_list_vc = status_list.publish(
            did, status_list_id, status_list_lenght, list_type
        )
        data_key = f"{label}:status_lists:{list_type}"
        await askar.store_data(settings.ASKAR_KEY, data_key, status_list_vc)
        data_key = f"{label}:status_entries:{list_type}"
        await askar.store_data(
            settings.ASKAR_KEY, data_key, [0, status_list_lenght - 1]
        )

    # Generate client credentials and store hash
    client_id, client_secret, client_hash = new_client(label)
    await askar.append_client_hash(settings.ASKAR_KEY, client_hash)

    return {
        "did": did,
        "client_id": client_id,
        "client_secret": client_secret,
        "service_endpoint": f"{settings.HTTPS_BASE}/organization/{label}",
        "token_endpoint": f"{settings.HTTPS_BASE}/oauth/token",
        "token_audience": f"{settings.HTTPS_BASE}",
    }


@router.get(
    "/organization/{label}/did.json",
    tags=["Identifiers"],
    summary="Get a DID's latest keys, services and capabilities",
)
async def get_did(label: str):
    label = format_label(label)
    try:
        data_key = f"{label}:did_document"
        did_doc = await askar.fetch_data(settings.ASKAR_KEY, data_key)
        return did_doc
    except:
        raise ValidationException(
            status_code=404,
            content={"message": f"Did not found"},
        )


@router.get(
    "/organization/{label}/identifiers/{did}",
    tags=["Identifiers"],
    dependencies=[Depends(JWTBearer())],
    summary="Get a DID's latest keys, services and capabilities",
)
async def get_did(label: str, did: str, request: Request):
    label = is_authorized(label, request)
    did = did.replace("%3", ":").strip().lower()
    valid_did(did)
    did_doc = agent.resolve_did(did)

    return {"didDocument": did_doc}
