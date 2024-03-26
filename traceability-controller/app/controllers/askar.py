import json
from aries_askar import Store, error
from config import settings
import time
from app.validations import ValidationException
from aries_askar.bindings import generate_raw_key

class AskarController:
    
    def __init__(self, db=settings.ASKAR_DEFAULT_DB):
        self.db = f'{settings.POSTGRES_URI}/{db}'
        self.key = generate_raw_key(settings.TRACTION_API_KEY)

    async def provision(self):
        await Store.provision(
            self.db,
            "raw",
            self.key,
            recreate=False,
        )

    async def open(self):
        return await Store.open(self.db, "raw", self.key)

    async def fetch(self, data_key):
        store = await self.open()
        async with store.session() as session:
            data = await session.fetch("seq", data_key)
        return json.loads(data.value)

    async def store(self, data_key, data):
        store = await self.open()
        async with store.session() as session:
            await session.insert(
                "seq",
                data_key,
                json.dumps(data),
                {"~plaintag": "a", "enctag": "b"},
            )

    async def update(self, data_key, data):
        store = await self.open()
        async with store.session() as session:
            await session.replace(
                "seq",
                data_key,
                json.dumps(data),
                {"~plaintag": "a", "enctag": "b"},
            )


async def find_api_key(storeKey, apiKeyHash):
    store = await open_store(storeKey)
    async for row in store.scan("seq", {"~plaintag": "a", "enctag": "b"}):
        if "api_key" in row.name:
            pass


async def verify_client_hash(storeKey, clientHash):
    dataKey = "client_hashes"
    store = await open_store(storeKey)
    async with store.session() as session:
        clientHashes = await session.fetch("seq", dataKey.lower())
    clientHashes = json.loads(clientHashes.value) if clientHashes else []
    if clientHash not in clientHashes:
        return False
    return True


async def append_client_hash(storeKey, client_hash):
    dataKey = issuerClientHashesDataKey()
    store = await open_store(storeKey)
    async with store.session() as session:
        client_hashes = await session.fetch("seq", dataKey.lower())
    client_hashes = json.loads(client_hashes.value) if client_hashes else []
    client_hashes.append(client_hash)
    async with store.session() as session:
        try:
            await session.replace(
                "seq",
                dataKey.lower(),
                json.dumps(client_hashes),
                {"~plaintag": "a", "enctag": "b"},
            )
        except error.AskarError:
            await session.insert(
                "seq",
                dataKey.lower(),
                json.dumps(client_hashes),
                {"~plaintag": "a", "enctag": "b"},
            )


async def did_label_exists(storeKey, did_label):
    store = await open_store(storeKey)
    async for row in store.scan("seq", {"~plaintag": "a", "enctag": "b"}):
        if row.name == f"{did_label}:did_document":
            return True
    return False


async def verify_token(storeKey, did_label, token):
    token = token.replace("Bearer ", "")
    store = await open_store(storeKey)
    async for row in store.scan("seq", {"~plaintag": "a", "enctag": "b"}):
        if row.name == f"{did_label}:oauth".lower():
            oauthData = json.loads(row.value.decode("utf-8"))
    if oauthData["access_token"] == token and oauthData["token_expiration"] >= int(
        time.time()
    ):
        return True
    raise ValidationException(
        status_code=401, content={"message": "Invalid or expired token"}
    )


async def get_credential(did_label, credentialId):
    try:
        dataKey = issuedCredentialDataKey(did_label, credentialId)
        return await fetch_data(settings.ASKAR_PUBLIC_STORE_KEY, dataKey)
    except:
        raise ValidationException(
            status_code=404,
            content={"message": f"credential {credentialId} not found"},
        )
