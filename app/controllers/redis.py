import redis, json, hashlib
from config import settings


def connect_client():
    return redis.Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
    )


def set_data(key, data):
    client = connect_client()
    client.set(key, data)


def get_data(key):
    client = connect_client()
    data = client.get(key)
    return data


def set_json_item(key, data):
    client = connect_client()
    client.set(key, json.dumps(data))


def get_json_item(key):
    client = connect_client()
    data = client.get(key)
    return json.loads(data)


def store_client_info(client_id, client_label, client_secret):
    client = connect_client()
    key = f"{client_id}:clientInfo:label"
    client.set(key, str(client_label))
    key = f"{client_id}:clientInfo:secretHash"
    client_secret_hash = hashlib.md5(client_secret).decode("utf-8")
    client.set(key, str(client_secret_hash))


def get_client_secret(client_id):
    client = connect_client()
    client_secret_hash = client.get(f"{client_id}:clientInfo:secretHash")
    return client_secret_hash


def get_client_label(client_id):
    client = connect_client()
    label = client.get(f"{client_id}:clientInfo:label")
    return label


def store_did_doc(org_label, did_doc):
    client = connect_client()
    key = f"{org_label}:didDoc"
    client.set(key, json.dumps(did_doc))


def get_did_doc(org_label):
    client = connect_client()
    did_doc = client.get(f"{org_label}:didDoc")
    return json.loads(did_doc)


def store_credential(org_label, credential):
    client = connect_client()
    key = f'{org_label}:credentials:{credential["id"]}'
    client.set(key, json.dumps(credential))


def get_credential(org_label, credential_id):
    client = connect_client()
    vc = client.get(f"{org_label}:credentials:{credential_id}")
    return json.loads(vc)


def store_status_list(org_label, status_list_vc):
    client = connect_client()
    key = f'{org_label}:statusLists:{status_list_vc["id"]}'
    data = json.dumps(status_list_vc)
    client.set(key, data)


def get_status_list(org_label, status_list_id):
    client = connect_client()
    status_list = client.get(f"{org_label}:statusLists:{status_list_id}")
    return json.loads(status_list)


def store_status_entries(org_label, status_list_entries, status_list_id):
    client = connect_client()
    key = f"{org_label}:statusEntries:{status_list_id}"
    data = json.dumps(status_list_entries)
    client.set(key, data)


def get_status_entries(org_label, status_list_id):
    client = connect_client()
    entries = client.get(f"{org_label}:statusEntries:{status_list_id}")
    return json.loads(entries)
