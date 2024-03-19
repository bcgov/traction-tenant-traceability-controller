from app.controllers import askar, agent
from app.models.did_document import DidDocument
from app.validations import ValidationException
from config import settings


def from_org_id(did_label):
    return f"{settings.DID_WEB_BASE}:{settings.DID_NAMESPACE}:{did_label}"


def can_issue(credential, did_label):
    """Function to check if the issuer field matches the organization's instance"""
    did = (
        credential["issuer"]
        if isinstance(credential["issuer"], str)
        else credential["issuer"]["id"]
    )
    if did != from_org_id(did_label):
        raise ValidationException(
            status_code=400, content={"message": "Invalid issuer"}
        )
    return did


async def register(did_label):
    # Create did uri
    did = from_org_id(did_label)

    # TODO, change to web
    verkey = agent.create_did("sov", "ed25519", did)

    # Create did document
    didDocument = DidDocument(id=did)
    didDocument.add_service("TraceabilityAPI")
    didDocument.add_verkey(verkey, "Ed25519VerificationKey2018")
    didDocument = didDocument.model_dump(by_alias=True, exclude_none=True)

    # Store did document
    dataKey = askar.didDocumentDataKey(did_label)
    await askar.store_data(settings.ASKAR_PUBLIC_STORE_KEY, dataKey, didDocument)


async def get_did_document(did_label):
    try:
        dataKey = askar.didDocumentDataKey(did_label)
        return await askar.fetch_data(settings.ASKAR_PUBLIC_STORE_KEY, dataKey)
    except:
        raise ValidationException(
            status_code=404,
            content={"message": f"DID not found"},
        )
