import uvicorn
from app.controllers.askar import AskarController
import asyncio

if __name__ == "__main__":
    asyncio.run(AskarController().provision())
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
    )
