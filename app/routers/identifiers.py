from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from app.models import CreateDIDWebInput
from app.controllers import agent, redis, status_list, did_web
from app.validations import ValidationException
from config import settings
from app.models import *
from app.auth.bearer import JWTBearer
from app.auth.handler import decodeJWT
from urllib import parse

router = APIRouter()


@router.post(
    "/register",
    tags=["Identifiers"],
    dependencies=[Depends(JWTBearer())],
    summary="Create Web DID",
)
async def register(request_body: CreateDIDWebInput, request: Request):
    token = request.headers.get("Authorization")
    agent.verify_token(token)

    request_body = await request.json()

    # Remove spacing and lowercase the label
    label = parse.quote(request_body["label"].strip().lower())
    # Creates a did:web identifier of the following form;
    # did:web:{domain}:organization:{label} -> did:web:example.com:organization:abc
    did = did_web.from_label(label)
    # Register with agent using the sov method
    verkey = agent.create_did("sov", "ed25519", did, token)

    # # PLACEHOLDER -> create a new client for controlling this did
    # client_id = uuid.uuid1()
    # client_secret = secrets.token_urlsafe(16)
    # redis.store_client_info(label, client_id, client_secret)

    # Create and store did document
    did_doc = {
        # This should have traceability context uncommented, currently creates an error when framing with pyld
        "@context": [
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/v2",
            # "https://w3id.org/traceability/v1",
        ],
        "id": did,
        "alsoKnownAs": [],
        "authentication": [f"{did}#verkey"],
        "assertionMethod": [f"{did}#verkey"],
        "verificationMethod": [
            {
                "id": f"{did}#verkey",
                "type": "Ed25519VerificationKey2018",
                "controller": did,
                "publicKeyBase58": verkey,
            }
        ],
        "service": [
            {
                "id": f"{did}#traceability-api",
                # This should be an array, currently creates an error when parsing with pydid
                # ["TraceabilityAPI"]
                "type": "TraceabilityAPI",
                "serviceEndpoint": f"{settings.HTTPS_BASE}/organization/{label}",
            }
        ],
    }
    redis.store_did_doc(label, did_doc)

    # Status list vc prep
    verkey = agent.get_verkey(did, token)
    options = {
        "verificationMethod": f"{did}#verkey",
        "proofPurpose": "AssertionMethod",
    }
    # Minimum bitstring lenght of 16KB
    lenght = settings.STATUS_LIST_LENGHT

    # RevocationList2020
    revocation_list_credential = status_list.create_credential(
        did, label, "RevocationList2020", lenght
    )
    revocation_list_vc = agent.sign_json_ld(
        revocation_list_credential, options, verkey, token
    )
    redis.store_status_list(label, revocation_list_vc)
    redis.store_status_entries(label, [0, lenght - 1], revocation_list_vc["id"])

    # StatusList2021
    status_list_credential = status_list.create_credential(
        did, label, "StatusList2021", lenght
    )
    status_list_vc = agent.sign_json_ld(status_list_credential, options, verkey, token)
    redis.store_status_list(label, status_list_vc)
    redis.store_status_entries(label, [0, lenght - 1], status_list_vc["id"])

    return {
        "didDocument": did_doc
    }


@router.get(
    "/organization/{label}/did.json",
    tags=["Identifiers"],
    summary="Get a DID's latest keys, services and capabilities",
)
async def get_did(label: str):
    label = parse.quote(label.strip().lower())
    try:
        did_doc = redis.get_did_doc(label)
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
    token = request.headers.get("Authorization")
    agent.verify_token(token)

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

    did_doc = agent.resolve_did(did, token)

    return {"didDocument": did_doc}
