import json


def success(message: str, raw: bool):
    if raw:
        headers = {
            "Content-Type": "text/plain"
        }
        body = "SUCCESS\n" + message
        response = {
            "statusCode": 200,
            "headers": headers,
            "body": body
        }
    else:
        headers = {
                "Content-Type": "application/json"
        }
        body = {
            "status": "SUCCESS",
            "message": message
        }
        response = {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(body)
        }
    return response

def fail(error: str, raw: bool):
    if raw:
        headers = {
            "Content-Type": "text/plain"
        }
        body = "FAIL\n" + str(error)
        response = {
            "statusCode": 200,
            "headers": headers,
            "body": body
        }
    else:
        headers = {
                "Content-Type": "application/json"
        }
        body = {
            "status": "FAIL",
            "message": str(error)
        }
        response = {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(body)
        }
    return response

def keyExists(element, *keys):
    _element = element
    for key in keys:
        try:
            _element = _element[key]
            if _element is None:
                return False
        except KeyError:
            return False
    return True
