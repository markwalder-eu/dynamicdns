from dynamicdns.models import Error
from dynamicdns.util import success, fail, keyExists


def handle(event, context):

    raw: bool = keyExists(event, 'queryStringParameters', 'raw')
    
    if not keyExists(event, 'requestContext', 'identity', 'sourceIp'):
        return fail(Error("Source IP address cannot be extracted from request context."), raw)
    sourceip: str = event['requestContext']['identity']['sourceIp']
    
    return success(sourceip, raw)
