import requests
from config import settings
from app.models.validations import ValidationException


def request_token():
    headers = {}
    body = {"api_key": settings.TRACTION_API_KEY}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/multitenancy/tenant/{settings.TRACTION_TENANT_ID}/token"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        token = r.json()["token"]
        return token
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def verify_token(token):
    headers = {"Authorization": token}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/tenant"
    r = requests.get(endpoint, headers=headers)
    try:
        return r.json()
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def create_api_key(did):
    token = f'Bearer {request_token()}'
    headers = {"Authorization": token}
    body = {"alias": did}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/tenant/authentications/api"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        api_id, api_key = r.json()["tenant_authentication_api_id"], r.json()["api_key"]
        return api_id, api_key
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def create_did(did_method, key_type, did=None):
    token = f'Bearer {request_token()}'
    headers = {"Authorization": token}
    body = {"method": did_method, "options": {"key_type": key_type, "did": did}}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/wallet/did/create"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        verkey = r.json()["result"]["verkey"]
        return verkey
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def resolve_did(did):
    # Custom did resolve until acapy can parse array service.type
    token = f'Bearer {request_token()}'
    did = did.replace("did:web:", "")
    did = did.replace(":", "/") if ":" in did else did + "/.well-known"
    did_endpoint = f"https://{did}/did.json"
    r = requests.get(did_endpoint)
    try:
        did_doc = r.json()
        return did_doc
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )

    # headers = {"Authorization": token}
    # endpoint = f"{settings.TRACTION_API_ENDPOINT}/resolver/resolve/{did}"
    # r = requests.get(endpoint, headers=headers)
    # try:
    #     did_doc = r.json()["did_document"]
    #     return did_doc
    # except:
    #     raise ValidationException(
    #         status_code=r.status_code, content={"message": r.text}
    #     )


def get_verkey(did):
    token = f'Bearer {request_token()}'
    headers = {"Authorization": token}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/wallet/did?did={did}"
    r = requests.get(endpoint, headers=headers)
    try:
        verkey = r.json()["results"][0]["verkey"]
        return verkey
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def sign_json_ld(credential, options, verkey):
    token = f'Bearer {request_token()}'
    headers = {"Authorization": token}
    body = {"doc": {"credential": credential, "options": options}, "verkey": verkey}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/jsonld/sign"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        vc = r.json()["signed_doc"]
        return vc
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def verify_json_ld(vc, verkey):
    token = f'Bearer {request_token()}'
    headers = {"Authorization": token}
    body = {"doc": vc, "verkey": verkey}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/jsonld/verify"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        response = r.json()
        return response
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def issue_credential(credential, options):
    token = f'Bearer {request_token()}'
    headers = {"Authorization": token}
    body = {"credential": credential, "options": options}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/vc/credentials/issue"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        vc = r.json()["vc"]
        return vc
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def verify_credential(vc):
    # token = f'Bearer {request_token()}'
    # headers = {"Authorization": token}
    headers = {"X-API-KEY": settings.VERIFIER_API_KEY}
    body = {"verifiableCredential": vc, "options": {}}
    # DID document can't contain traceability context
    # traceability service type must be a string (not an array)
    endpoint = f"{settings.VERIFIER_ENDPOINT}/vc/credentials/verify"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        verified = r.json()
        return verified
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def verify_presentation(vp):
    # token = f'Bearer {request_token()}'
    # headers = {"Authorization": token}
    headers = {"X-API-KEY": settings.VERIFIER_API_KEY}
    body = {"verifiablePresentation": vp, "options": {}}
    # DID document can't contain traceability context
    # traceability service type must be a string (not an array)
    endpoint = f"{settings.VERIFIER_ENDPOINT}/vc/presentations/verify"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        verified = r.json()
        return verified
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )
