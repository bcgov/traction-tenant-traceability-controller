from fastapi import FastAPI, APIRouter
from config import settings

app = FastAPI(
    title=settings.PROJECT_TITLE,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
    contact=settings.PROJECT_CONTACT,
    license_info=settings.PROJECT_LICENSE_INFO,
)

api_router = APIRouter()

@api_router.get("/")
async def index():
    return {"status": "ok"}

app.include_router(api_router)