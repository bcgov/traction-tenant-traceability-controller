from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from aries_askar.bindings import generate_raw_key

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Settings(BaseSettings):
    PROJECT_TITLE: str = "aries-traceability-api"
    PROJECT_VERSION: str = "v0"

    TRACEABILITY_DOMAIN_NAME: str = os.environ["TRACEABILITY_DOMAIN_NAME"]
    DID_WEB_BASE: str = f"did:web:{TRACEABILITY_DOMAIN_NAME}"
    HTTPS_BASE: str = f"https://{TRACEABILITY_DOMAIN_NAME}"

    TRACTION_API_ENDPOINT: str = os.environ["TRACTION_API_ENDPOINT"]
    TRACTION_TENANT_ID: str = os.environ["TRACTION_TENANT_ID"]
    TRACTION_API_KEY: str = os.environ["TRACTION_API_KEY"]

    TRACEABILITY_ADMIN_API_KEY: str = os.environ["TRACEABILITY_ADMIN_API_KEY"]

    # Minimum lenght of 16KB
    STATUS_LIST_LENGHT: int = 131072

    POSTGRES_URI: str = os.environ["POSTGRES_URI"]
    ASKAR_KEY: str = generate_raw_key(os.environ["ASKAR_SEED"])

    VERIFIER_ENDPOINT: str = os.environ["VERIFIER_ENDPOINT"]
    VERIFIER_API_KEY: str = os.environ["VERIFIER_API_KEY"]

    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET: str = os.environ["JWT_SECRET"]


settings = Settings()
