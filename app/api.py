from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.models.validations import ValidationException
from app.routers import authentication, identifiers, credentials, presentations
from config import settings

app = FastAPI(title=settings.PROJECT_TITLE, version=settings.PROJECT_VERSION)


api_router = APIRouter()

api_router.include_router(authentication.router)
api_router.include_router(identifiers.router)
api_router.include_router(credentials.router)
api_router.include_router(presentations.router)

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
        "location": errors["loc"]
    }
    if errors["msg"] == 'Value error, Unknown issuer':
        return JSONResponse(error, status_code=422)
    return JSONResponse(error, status_code=400)
