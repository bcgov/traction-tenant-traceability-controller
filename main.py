import uvicorn
from app.controllers import askar
from config import settings
import asyncio

if __name__ == "__main__":
    # Provision askar public store
    asyncio.run(askar.provision_public_store())
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=int(settings.PORT),
        workers=int(settings.WORKERS),
    )
