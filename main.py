import uvicorn
import os
from dotenv import load_dotenv
from app.controllers import askar
import asyncio

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

port = int(os.environ["TRACEABILITY_API_PORT"])
workers = int(os.environ["WORKERS"])

if __name__ == "__main__":
    # Provision askar store
    asyncio.run(askar.provision_store(os.environ["ASKAR_KEY"]))
    uvicorn.run("app.api:app", host="0.0.0.0", port=port, workers=workers)
