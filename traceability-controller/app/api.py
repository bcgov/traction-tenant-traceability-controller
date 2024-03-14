from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.validations import ValidationException
from app.routers import authentication, identifiers, credentials, presentations
from config import settings

app = FastAPI(title=settings.PROJECT_TITLE, version=settings.PROJECT_VERSION)


api_router = APIRouter()

api_router.include_router(authentication.router)
api_router.include_router(identifiers.router, prefix=f"/{settings.DID_NAMESPACE}")
api_router.include_router(credentials.router, prefix=f"/{settings.DID_NAMESPACE}")
api_router.include_router(presentations.router, prefix=f"/{settings.DID_NAMESPACE}")


@api_router.get("/server/health", tags=["Server"], summary="Health check")
async def health_check():
    return JSONResponse(status_code=200, content={})

@api_router.get("/server/status", tags=["Server"], summary="Status check")
async def status_check():
    return JSONResponse(status_code=200, content={})

@api_router.get("/server/live", tags=["Server"], summary="Live check")
async def live_check():
    return JSONResponse(status_code=200, content={})


app.include_router(api_router)


# Custom handlers for test-suite conformance
@app.exception_handler(ValidationException)
async def validation_exception_handler(
    request: Request, exception: ValidationException
):
    return JSONResponse(
        status_code=exception.status_code,
        content=exception.content,
    )


@app.exception_handler(RequestValidationError)
async def custom_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()[0]
    error = {
        "message": errors["msg"],
        "type": errors["type"],
        "location": errors["loc"],
    }
    if errors["msg"] == "Value error, Unknown issuer":
        return JSONResponse(error, status_code=422)
    return JSONResponse(error, status_code=400)
