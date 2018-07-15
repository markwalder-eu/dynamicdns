import json

import dynamicdns


def handle(event, context):
    headers = {
            "Content-Type": "application/json"
    }
    body = {
        "version":      dynamicdns.__version__,
        "author":       dynamicdns.__author__,
        "author-email": dynamicdns.__author_email__
    } 
    response = {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps(body)
    }
    return response
