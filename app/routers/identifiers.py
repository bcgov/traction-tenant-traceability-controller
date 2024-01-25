from fastapi import APIRouter, Depends, Request, Security
from app.models.web_requests import CreateDIDWebInput
from app.models.did_document import DidDocument
from app.models.validations import ValidationException
from app.controllers import askar, agent, status_list
from config import settings
from app.auth.bearer import JWTBearer
from app.auth.handler import get_api_key, is_authorized
from ..utils import format_label
import hashlib, uuid

router = APIRouter()


@router.post(
    "/did",
    tags=["Identifiers"],
    summary="Create Web DID",
)
async def register(request_body: CreateDIDWebInput, request: Request, api_key: str = Security(get_api_key)):

    request_body = await request.json()

    # Create a did:web identifier and register with traction
    label = format_label(request_body["label"])
    did = f"{settings.DID_WEB_BASE}:organization:{label}"
    verkey = agent.create_did("sov", "ed25519", did)

    # Create and store did document
    did_doc = DidDocument(id=did)
    did_doc.add_verkey(verkey)
    did_doc.add_service('TraceabilityAPI')

    data_key = f"{label}:did_document"
    await askar.store_data(settings.ASKAR_KEY, data_key, dict(did_doc))

    # Publish Status List VC
    status_list_id = f"{settings.HTTPS_BASE}/organization/{label}/credentials/status/revocation"
    status_list_lenght = settings.STATUS_LIST_LENGHT
    status_list_credential = status_list.create_credential(
        did, status_list_id, status_list_lenght
    )
    options = {
        "verificationMethod": f"{did}#verkey",
        "proofPurpose": "AssertionMethod",
    }
    verkey = agent.get_verkey(did)
    status_list_vc = agent.sign_json_ld(
        status_list_credential, options, verkey
    )

    data_key = f"{label}:status_list"
    await askar.store_data(settings.ASKAR_KEY, data_key, status_list_vc)
    data_key = f"{label}:status_entries"
    await askar.store_data(settings.ASKAR_KEY, data_key, [0, status_list_lenght - 1])

    # Generate client credentials and store hash
    client_id = hashlib.md5(label.encode()).hexdigest()
    client_secret = uuid.uuid4()
    client_hash = str(uuid.uuid5(client_secret, client_id))
    await askar.append_client_hash(settings.ASKAR_KEY, client_hash)

    return {
        "did": did,
        "client_id": client_id, 
        "client_secret": client_secret, 
        }


@router.get(
    "/organization/{label}/did.json",
    tags=["Identifiers"],
    summary="Get a DID's latest keys, services and capabilities",
)
async def get_did(label: str):
    label = format_label(label)
    try:
        data_key = f"{label}:did_document".lower()
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
    token = request.headers.get("Authorization").replace("Bearer ", "")
    if not is_authorized(token, label):
        raise ValidationException(
            status_code=401, content={"message": "Unauthorized"}
        )

    did = did.replace("%3", ":").strip().lower()
    if "urn:uuid:" in did:
        raise ValidationException(
            status_code=404,
            content={"message": f"{did} not found"},
        )
    if "did:" not in did:
        raise ValidationException(
            status_code=400, content={"message": "Invalid DID format"}
        )
    did_doc = agent.resolve_did(did)

    return {"didDocument": did_doc}
