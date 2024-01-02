from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from app.routers import authentication, identifiers, credentials, presentations
from app.validations import ValidationException
from config import settings

app = FastAPI(title=settings.PROJECT_TITLE, version=settings.PROJECT_VERSION)


# Custom handler for test-suite conformance
@app.exception_handler(ValidationException)
async def validation_exception_handler(
    request: Request, exception: ValidationException
):
    return JSONResponse(
        status_code=exception.status_code,
        content=exception.content,
    )


api_router = APIRouter()

api_router.include_router(authentication.router)
api_router.include_router(identifiers.router)
api_router.include_router(credentials.router)
api_router.include_router(presentations.router)

app.include_router(api_router)
