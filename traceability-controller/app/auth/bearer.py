from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.validations import ValidationException
from .handler import decodeJWT


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise ValidationException(
                    status_code=401, content={"message": "Invalid or expired token"}
                )
            if not self.verify_jwt(credentials.credentials):
                raise ValidationException(
                    status_code=401, content={"message": "Invalid or expired token"}
                )
            return credentials.credentials
        else:
            raise ValidationException(
                status_code=401, content={"message": "Invalid or expired token"}
            )

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
