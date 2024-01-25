import requests
from config import settings
from app.validations import ValidationException


def request_token(tenant_id, api_key):
    headers = {}
    body = {"api_key": api_key}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/multitenancy/tenant/{tenant_id}/token"
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


def create_api_key(label, token):
    headers = {"Authorization": token}
    body = {"alias": label}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/tenant/authentications/api"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        api_id, api_key = r.json()["tenant_authentication_api_id"], r.json()["api_key"]
        return api_id, api_key
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def create_did(did_method, key_type, did=None, token=None):
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


def resolve_did(did, token):
    # Custom did resolve until acapy can parse array service.type
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


def get_verkey(did, token):
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


def sign_json_ld(credential, options, verkey, token):
    headers = {"Authorization": token}
    body = {"doc": {"credential": credential, "options": options}, "verkey": verkey}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/jsonld/sign"
    try:
        r = requests.post(endpoint, headers=headers, json=body)
        vc = r.json()["signed_doc"]
        return vc
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def verify_json_ld(vc, verkey, token):
    headers = {"Authorization": token}
    body = {"doc": vc, "verkey": verkey}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/jsonld/verify"
    try:
        r = requests.post(endpoint, headers=headers, json=body)
        response = r.json()
        return response
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def issue_credential(credential, options, token):
    headers = {"Authorization": token}
    body = {"credential": credential, "options": options}
    endpoint = f"{settings.TRACTION_API_ENDPOINT}/vc/ldp/issue"
    r = requests.post(endpoint, headers=headers, json=body)
    try:
        vc = r.json()["vc"]
        return vc
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def verify_credential(vc, token):
    # headers = {"Authorization": token}
    headers = {}
    body = {"vc": vc, "options": {}}
    # DID document can't contain traceability context
    # traceability service type must be a string (not an array)
    endpoint = f"{settings.VERIFIER_AGENT}/vc/ldp/verify"
    try:
        r = requests.post(endpoint, headers=headers, json=body)
        verified = r.json()
        return verified
    except:
        raise ValidationException(
            status_code=r.status_code, content={"message": r.text}
        )


def create_presentation(presentation, token):
    pass
