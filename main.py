import uvicorn
import os
from dotenv import load_dotenv
from app.controllers import askar
from config import settings
import asyncio

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

if __name__ == "__main__":
    # Provision askar store
    asyncio.run(askar.provision_store(settings.ASKAR_KEY))
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, workers=4)
