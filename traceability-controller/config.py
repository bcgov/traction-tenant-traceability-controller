from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Settings(BaseSettings):
    PROJECT_TITLE: str = "traction-tenant-traceability-controller"
    PROJECT_VERSION: str = "v0"

    DOMAIN: str = os.environ["TRACEABILITY_CONTROLLER_DOMAIN"]
    DID_NAMESPACE: str = "organization"
    HTTPS_BASE: str = f"https://{DOMAIN}"
    DID_WEB_BASE: str = f"did:web:{DOMAIN}"

    TRACTION_API_KEY: str = os.environ["TRACTION_API_KEY"]
    TRACTION_TENANT_ID: str = os.environ["TRACTION_TENANT_ID"]
    TRACTION_API_ENDPOINT: str = os.environ["TRACTION_API_ENDPOINT"]

    # We use the traction api key as the controller admin api key
    TRACEABILITY_ADMIN_API_KEY: str = TRACTION_API_KEY
    # Minimum lenght of 16KB
    STATUS_LIST_LENGHT: int = 200000

    POSTGRES_URI: str = os.environ["POSTGRES_URI"]

    # We derive the public storage askar key from the traction api key
    ASKAR_DEFAULT_DB: str = 'traceability'

    # To be removed when new routes are added to traction
    VERIFIER_ENDPOINT: str = os.environ["VERIFIER_ENDPOINT"]
    VERIFIER_API_KEY: str = TRACTION_API_KEY

    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET: str = TRACTION_API_KEY


settings = Settings()
