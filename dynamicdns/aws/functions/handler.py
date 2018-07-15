from dynamicdns.util import (success, fail, keyExists)
from dynamicdns.aws.functions import (dns, myip, script, version)


def execute(resource: str, method: str, event: dict, context: dict):
    return  {   "/dns|POST":        dns.handle,
                "/myip|GET":        myip.handle,
                "/script|GET":      script.handle,
                "/version|GET":     version.handle,
                "/info|GET":        info,
            }.get(resource + "|" + method, executefail)(event, context)


def info(event: dict, context: dict):
    return success(event, False)


def executefail(event: dict, context: dict):
    raw: bool = keyExists(event, 'queryStringParameters', 'raw')
    return fail("Resource / Handler mapping not found.", raw)


def handle(event, context):
    resource = event['resource']
    method = event['httpMethod']
    return execute(resource, method, event, context)
