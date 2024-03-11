import json
from aries_askar import Store, error
from config import settings
import time
from app.validations import ValidationException


def holderClientHashesDataKey(did_label):
    """OAuth client who will send presentations `/presentations`"""
    return f"holderClientHashes"


def issuerClientHashesDataKey():
    """OAuth client who will issue credentials `/credentials/issue`"""
    return f"issuerClientHashes"


def didDocumentDataKey(did_label):
    """Controller documents for web DIDs"""
    return f"didDocuments:{did_label}"


def statusEntriesDataKey(did_label, statusCredentialId):
    """List of registered indexes in a status list"""
    return f"statusEntries:{did_label}:{statusCredentialId}"


def statusCredentialDataKey(did_label, statusCredentialId):
    """Status list credential maintained by an issuer"""
    return f"statusCredentials:{did_label}:{statusCredentialId}"


def issuedCredentialDataKey(did_label, credentialId):
    """Issued credentials of an issuer"""
    return f"issuedCredentials:{did_label}:{credentialId}"


def recievedCredentialDataKey(did_label, credentialId):
    """Credentials recieved through a presentation exchange"""
    return f"storedCredentials:{did_label}:{credentialId}"


async def provision_public_store():
    await Store.provision(
        settings.ASKAR_PUBLIC_STORE,
        "raw",
        settings.ASKAR_PUBLIC_STORE_KEY,
        recreate=False,
    )


async def open_store(key):
    return await Store.open(settings.ASKAR_PUBLIC_STORE, "raw", key)


async def store_data(storeKey, dataKey, data):
    store = await open_store(storeKey)
    async with store.session() as session:
        await session.insert(
            "seq",
            dataKey.lower(),
            json.dumps(data),
            {"~plaintag": "a", "enctag": "b"},
        )


async def fetch_data(storeKey, dataKey):
    store = await open_store(storeKey)
    async with store.session() as session:
        data = await session.fetch("seq", dataKey.lower())
    return json.loads(data.value)


async def update_data(storeKey, dataKey, new_data):
    store = await open_store(storeKey)
    async with store.session() as session:
        await session.replace(
            "seq",
            dataKey.lower(),
            json.dumps(new_data),
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
