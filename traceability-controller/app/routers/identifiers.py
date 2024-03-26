from fastapi import APIRouter, Depends, Request, Security
from fastapi.responses import JSONResponse
from app.models.web_requests import CreateDIDWebInput
from app.controllers import auth
from app.controllers.traction import TractionController
from app.controllers.askar import AskarController
from config import settings
from app.utils import did_from_label
from app.auth.bearer import JWTBearer
from app.auth.handler import get_api_key
import uuid

router = APIRouter()


@router.post("/", tags=["Identifiers"], summary="Create Web DID")
async def register_org_did(
    request_body: CreateDIDWebInput,
    apiKey: str = Security(get_api_key),
):
    label = vars(request_body)["label"]
    
    # Generate uuid if no label was provided
    did_label = label if label else str(uuid.uuid4())

    traction = TractionController(did_label)
    await traction.create_did()
    await traction.create_status_list()

    # Generate client credentials and store hash
    client_id, client_secret = await auth.new_issuer_client(did_label)
    response = {
        "did": did_from_label(did_label),
        "client_id": str(client_id),
        "client_secret": client_secret,
        "token_audience": f"{settings.HTTPS_BASE}",
        "token_endpoint": f"{settings.HTTPS_BASE}/oauth/token",
        "service_endpoint": f"{settings.HTTPS_BASE}/{settings.DID_NAMESPACE}/{did_label}",
    }

    return JSONResponse(status_code=201, content=response)


@router.get(
    "/{did_label}/did.json",
    tags=["Identifiers"],
    summary="Get a DID's latest keys, services and capabilities",
)
async def get_did(did_label: str):
    did = did_from_label(did_label)
    did_document = {
        '@context': [
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/v2",
            "https://w3id.org/traceability/v1"
        ],
        'id': did,
        'verificationMethod': [{
            'id': f'{did}#verkey',
            'type': 'Ed25519VerificationKey2018',
            'controller': did,
            'publicKeyBase58': await AskarController(did_label).fetch('verkey')
        }],
        'authentication': [ f'{did}#verkey'],
        'assertionMethod': [ f'{did}#verkey'],
        'service': [{
            'id': f'{did}#traceability-api',
            'type': ["TraceabilityAPI"],
            'serviceEndpoint': f'{settings.HTTPS_BASE}/{settings.DID_NAMESPACE}/{did_label}'
        }]
    }
    return JSONResponse(status_code=200, content=did_document)


@router.get(
    "/{did_label}/identifiers/{did}",
    tags=["Identifiers"],
    dependencies=[Depends(JWTBearer())],
    summary="Get a DID's latest keys, services and capabilities",
)
async def get_did(did_label: str, did: str, request: Request):
    await auth.is_authorized(did_label, request)
    response = {"didDocument": TractionController(did_label).resolve_did(did)}
    return JSONResponse(status_code=200, content=response)
