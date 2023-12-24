from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Settings(BaseSettings):
    PROJECT_TITLE: str = "status-list api server"
    PROJECT_VERSION: str = "v0"
    PROJECT_DESCRIPTION: str = """
    Status-list api server
    """
    PROJECT_CONTACT: dict = {
        "name": "OpSecId",
        "url": "https://github.com/OpSecId",
    }
    PROJECT_LICENSE_INFO: dict = {
        "name": "Apache License",
        "url": "https://github.com/OpSecId/aries-traceability/blob/main/LICENSE"
    }

settings = Settings()