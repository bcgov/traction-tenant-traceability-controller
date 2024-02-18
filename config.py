from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from aries_askar.bindings import generate_raw_key

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Settings(BaseSettings):
    PROJECT_TITLE: str = "aries-traceability-controller"
    PROJECT_VERSION: str = "v0"

    TRACEABILITY_DOMAIN_NAME: str = os.environ["TRACEABILITY_DOMAIN_NAME"]
    DID_WEB_BASE: str = f"did:web:{TRACEABILITY_DOMAIN_NAME}"
    HTTPS_BASE: str = f"https://{TRACEABILITY_DOMAIN_NAME}"

    TRACTION_API_ENDPOINT: str = os.environ["TRACTION_API_ENDPOINT"]
    TRACTION_TENANT_ID: str = os.environ["TRACTION_TENANT_ID"]
    TRACTION_API_KEY: str = os.environ["TRACTION_API_KEY"]

    # We use the traction api key as the controller admin api key
    TRACEABILITY_ADMIN_API_KEY: str = os.environ["TRACTION_API_KEY"]
    # Minimum lenght of 16KB
    STATUS_LIST_LENGHT: int = 200000

    POSTGRES_URI: str = os.environ["POSTGRES_URI"]

    # We derive the public storage askar key from the traction api key
    ASKAR_KEY: str = generate_raw_key(os.environ["TRACTION_API_KEY"])

    # To be removed when new routes are added to traction
    VERIFIER_ENDPOINT: str = os.environ["VERIFIER_ENDPOINT"]
    VERIFIER_API_KEY: str = os.environ["TRACTION_API_KEY"]

    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET: str = os.environ["TRACTION_API_KEY"]


settings = Settings()
