import uvicorn
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

port = int(os.environ["PORT"])
workers = int(os.environ["WORKERS"])

if __name__ == "__main__":
    uvicorn.run("app.api:app", host="0.0.0.0", port=port, workers=workers)
