from urllib import parse
from config import settings


def from_label(label):
    label = parse.quote(label.strip().lower())
    did_web = f"{settings.DID_WEB_BASE}:organization:{label}"
    return did_web
