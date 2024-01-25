import json
from aries_askar import Store
from config import settings

async def provision_store(key):
    await Store.provision(settings.POSTGRES_URI, "raw", key, recreate=False)

async def open_store(key):
    store = await Store.open(settings.POSTGRES_URI, "raw", key)
    return store

async def store_data(store_key, data_key, data):
    store = await open_store(store_key)
    async with store.session() as session:
        await session.insert(
                "seq",
                data_key,
                json.dumps(data),
                {"~plaintag": "a", "enctag": "b"},
            )

async def fetch_data(store_key, data_key):
    store = await open_store(store_key)
    async with store.session() as session:
        data = await session.fetch("seq", data_key)
    return json.loads(data.value)
    
async def update_data(store_key, data_key, new_data):
    store = await open_store(store_key)
    async with store.session() as session:
        await session.replace("seq", data_key, json.dumps(new_data), {"~plaintag": "a", "enctag": "b"})

