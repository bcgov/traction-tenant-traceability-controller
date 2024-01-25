import re


class ValidationException(Exception):
    def __init__(self, content: dict, status_code: int):
        self.content = content
        self.status_code = status_code


def valid_xml_timestamp(timestamp):
    iso8601_regex = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
    match_iso8601 = re.compile(iso8601_regex).match
    try:
        if match_iso8601(timestamp) is None:
            return False
    except:
        pass
    return True


def valid_type(type):
    if type.isspace():
        return False
    if " " in type:
        return False
    return True


def identifiers_resolve(did):
    # TODO, could be better
    if did[:9] == "urn:uuid:":
        raise ValidationException(status_code=404, content={"message": "Not found"})
    if "did:" not in did:
        raise ValidationException(status_code=400, content={"message": "Invalid DID"})

    return True