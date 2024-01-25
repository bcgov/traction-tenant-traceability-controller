from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Settings(BaseSettings):
    PROJECT_TITLE: str = "aries-traceability-api"
    PROJECT_VERSION: str = "v0"

    TRACTION_API_ENDPOINT: str = os.environ["TRACTION_API_URL"]
    TRACTION_TENANT_ID: str = os.environ["TRACTION_TENANT_ID"]
    TRACTION_API_KEY: str = os.environ["TRACTION_API_KEY"]

    TRACEABILITY_API_ENDPOINT: str = os.environ["TRACEABILITY_API_ENDPOINT"]
    DID_WEB_BASE: str = f"did:web:{TRACEABILITY_API_ENDPOINT}"
    HTTPS_BASE: str = f"https://{TRACEABILITY_API_ENDPOINT}"

    # Minimum lenght of 16KB
    STATUS_LIST_LENGHT: int = 131072

    REDIS_HOST: str = os.environ["REDIS_HOST"]
    REDIS_PORT: str = os.environ["REDIS_PORT"]

    JWT_ALGORITHM: str = os.environ["JWT_ALGORITHM"]
    JWT_SECRET: str = os.environ["JWT_SECRET"]
    
    VERIFIER_AGENT: str = os.environ["VERIFIER_AGENT"]


settings = Settings()
