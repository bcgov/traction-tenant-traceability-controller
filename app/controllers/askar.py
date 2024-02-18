import json
from aries_askar import Store, error
from config import settings
import time
from app.validations import ValidationException

        
def holderClientHashesDataKey(orgId):
    """ OAuth client who will send presentations `/presentations` """
    return f'holderClientHashes'

def issuerClientHashesDataKey():
    """ OAuth client who will issue credentials `/credentials/issue` """
    return f'issuerClientHashes'

def didDocumentDataKey(orgId):
    """ Controller documents for web DIDs """
    return f'didDocuments:{orgId}'

def statusEntriesDataKey(orgId, statusCredentialId):
    """ List of registered indexes in a status list """
    return f'statusEntries:{orgId}:{statusCredentialId}'

def statusCredentialDataKey(orgId, statusCredentialId):
    """ Status list credential maintained by an issuer """
    return f'statusCredentials:{orgId}:{statusCredentialId}'

def issuedCredentialDataKey(orgId, credentialId):
    """ Issued credentials of an issuer """
    return f'issuedCredentials:{orgId}:{credentialId}'

def recievedCredentialDataKey(orgId, credentialId):
    """ Credentials recieved through a presentation exchange """
    return f'storedCredentials:{orgId}:{credentialId}'

async def provision_store(key):
    await Store.provision(settings.POSTGRES_URI, "raw", key, recreate=False)


async def open_store(key):
    return await Store.open(settings.POSTGRES_URI, "raw", key)


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


async def orgId_exists(storeKey, orgId):
    store = await open_store(storeKey)
    async for row in store.scan("seq", {"~plaintag": "a", "enctag": "b"}):
        if row.name == f"{orgId}:did_document":
            return True
    return False


async def verify_token(storeKey, orgId, token):
    token = token.replace("Bearer ", "")
    store = await open_store(storeKey)
    async for row in store.scan("seq", {"~plaintag": "a", "enctag": "b"}):
        if row.name == f"{orgId}:oauth".lower():
            oauthData = json.loads(row.value.decode("utf-8"))
    if oauthData["access_token"] == token and oauthData["token_expiration"] >= int(
        time.time()
    ):
        return True
    raise ValidationException(
        status_code=401, content={"message": "Invalid or expired token"}
    )

async def get_credential(orgId, credentialId):
    try:
        dataKey = issuedCredentialDataKey(orgId, credentialId)
        return await fetch_data(settings.ASKAR_KEY, dataKey)
    except:
        raise ValidationException(
            status_code=404,
            content={"message": f"credential {credentialId} not found"},
        )