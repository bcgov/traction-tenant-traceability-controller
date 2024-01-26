import requests
from config import settings
from app.validations import ValidationException


def request_token():
    headers = {}
    body = {"api_key": settings.TRACTION_API_KEY}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/multitenancy/tenant/{settings.TRACTION_TENANT_ID}/token"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        return r.json()["token"]
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
    headers = {"Authorization": f"Bearer {request_token()}"}
    body = {"alias": did}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/tenant/authentications/api"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        return r.json()["api_key"]
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def create_did(did_method, key_type, did=None):
    headers = {"Authorization": f"Bearer {request_token()}"}
    body = {"method": did_method, "options": {"key_type": key_type, "did": did}}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/wallet/did/create"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        return r.json()["result"]["verkey"]
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def resolve_did(did):
    headers = {"Authorization": f"Bearer {request_token()}"}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/resolver/resolve/{did}"
    r = requests.get(endpoint, headers=headers)
    try:
        return r.json()["did_document"]
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def get_verkey(did):
    headers = {"Authorization": f"Bearer {request_token()}"}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/wallet/did?did={did}"
    r = requests.get(endpoint, headers=headers)
    try:
        return r.json()["results"][0]["verkey"]
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def sign_json_ld(credential, options, verkey):
    headers = {"Authorization": f"Bearer {request_token()}"}
    body = {"doc": {"credential": credential, "options": options}, "verkey": verkey}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/jsonld/sign"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        return r.json()["signed_doc"]
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def verify_json_ld(vc, verkey):
    headers = {"Authorization": f"Bearer {request_token()}"}
    body = {"doc": vc, "verkey": verkey}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/jsonld/verify"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        return r.json()
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def issue_credential(credential, options):
    headers = {"Authorization": f"Bearer {request_token()}"}
    body = {"credential": credential, "options": options}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/vc/credentials/issue"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        return r.json()["vc"]
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def verify_credential(vc):
    # headers = {"Authorization": f'Bearer {request_token()}'}
    headers = {"X-API-KEY": settings.VERIFIER_API_KEY}
    body = {"verifiableCredential": vc, "options": {}}
    endpoint = f"{settings.VERIFIER_ENDPOINT}/vc/credentials/verify"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        return r.json()
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def verify_presentation(vp):
    # headers = {"Authorization": f'Bearer {request_token()}'}
    headers = {"X-API-KEY": settings.VERIFIER_API_KEY}
    body = {"verifiablePresentation": vp, "options": {}}
    endpoint = f"{settings.VERIFIER_ENDPOINT}/vc/presentations/verify"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        return r.json()
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )
