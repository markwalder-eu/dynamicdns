import json


def handle(event, context):
    headers = {
            "Content-Type": "application/json"
    }
    body = {
        "event":      event,
        "context":    context
    } 
    response = {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps(body)
    }
    return response
