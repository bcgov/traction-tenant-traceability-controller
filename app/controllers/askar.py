import json
from aries_askar import Store, error
from config import settings
import time
from app.validations import ValidationException


async def provision_store(key):
    await Store.provision(settings.POSTGRES_URI, "raw", key, recreate=False)


async def open_store(key):
    return await Store.open(settings.POSTGRES_URI, "raw", key)


async def store_data(store_key, data_key, data):
    store = await open_store(store_key)
    async with store.session() as session:
        await session.insert(
            "seq",
            data_key.lower(),
            json.dumps(data),
            {"~plaintag": "a", "enctag": "b"},
        )


async def fetch_data(store_key, data_key):
    store = await open_store(store_key)
    async with store.session() as session:
        data = await session.fetch("seq", data_key.lower())
    return json.loads(data.value)


async def update_data(store_key, data_key, new_data):
    store = await open_store(store_key)
    async with store.session() as session:
        await session.replace(
            "seq",
            data_key.lower(),
            json.dumps(new_data),
            {"~plaintag": "a", "enctag": "b"},
        )


async def find_api_key(store_key, api_key_hash):
    store = await open_store(store_key)
    async for row in store.scan("seq", {"~plaintag": "a", "enctag": "b"}):
        if "api_key" in row.name:
            print(api_key_hash)
            print(row.value)


async def verify_client_hash(store_key, client_hash):
    data_key = "client_hashes"
    store = await open_store(store_key)
    async with store.session() as session:
        client_hashes = await session.fetch("seq", data_key.lower())
    client_hashes = json.loads(client_hashes.value) if client_hashes else []
    if client_hash not in client_hashes:
        return False
    return True


async def append_client_hash(store_key, client_hash):
    data_key = "client_hashes"
    store = await open_store(store_key)
    async with store.session() as session:
        client_hashes = await session.fetch("seq", data_key.lower())
    client_hashes = json.loads(client_hashes.value) if client_hashes else []
    client_hashes.append(client_hash)
    async with store.session() as session:
        try:
            await session.replace(
                "seq",
                data_key.lower(),
                json.dumps(client_hashes),
                {"~plaintag": "a", "enctag": "b"},
            )
        except error.AskarError:
            await session.insert(
                "seq",
                data_key.lower(),
                json.dumps(client_hashes),
                {"~plaintag": "a", "enctag": "b"},
            )


async def label_exists(store_key, label):
    store = await open_store(store_key)
    async for row in store.scan("seq", {"~plaintag": "a", "enctag": "b"}):
        if row.name == f"{label}:did_document".lower():
            return True
    return False


async def verify_token(store_key, label, token):
    token = token.replace("Bearer ", "")
    store = await open_store(store_key)
    async for row in store.scan("seq", {"~plaintag": "a", "enctag": "b"}):
        if row.name == f"{label}:oauth".lower():
            oauth_data = json.loads(row.value.decode("utf-8"))
    if oauth_data["access_token"] == token and oauth_data["token_expiration"] >= int(
        time.time()
    ):
        return True
    raise ValidationException(
        status_code=401, content={"message": "Invalid or expired token"}
    )
