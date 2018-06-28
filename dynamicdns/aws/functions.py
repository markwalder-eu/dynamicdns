import os
import json

from dynamicdns.models import Error, ConfigProvider, DNSProvider
from dynamicdns.handler import Handler
from dynamicdns.util import success, fail, keyExists

from dynamicdns.aws.s3config import S3ConfigProvider
from dynamicdns.aws.route53 import Route53Provider


def info(event, context): # pragma: no cover
    config: ConfigProvider = S3ConfigProvider()
    config.load()
    dns: DNSProvider = Route53Provider(config)
    handler: Handler = Handler(dns)
    return AWSFunctions(config, dns, handler).info(event, context)

def local(event, context): # pragma: no cover
    config: ConfigProvider = S3ConfigProvider()
    config.load()
    dns: DNSProvider = Route53Provider(config)
    handler: Handler = Handler(dns)
    return AWSFunctions(config, dns, handler).local(event, context)


def remote(event, context): # pragma: no cover
    config: ConfigProvider = S3ConfigProvider()
    config.load()
    dns: DNSProvider = Route53Provider(config)
    handler: Handler = Handler(dns)
    return AWSFunctions(config, dns, handler).remote(event, context)


class AWSFunctions:

    def __init__(self, config: ConfigProvider, dns: DNSProvider, handler: Handler):
        self.config = config
        self.dns = dns
        self.handler = handler


    def info(self, event, context):
        return success(event, False)


    def local(self, event, context):
        
        raw: bool = keyExists(event, 'queryStringParameters', 'raw')
        
        if not keyExists(event, 'requestContext', 'identity', 'sourceIp'):
            return fail(Error("Source IP address cannot be extracted from request context."), raw)
        
        sourceip: str = event['requestContext']['identity']['sourceIp']
        
        return success(sourceip, raw)


    def remote(self, event, context):

        raw: bool = keyExists(event, 'queryStringParameters', 'raw')

        if not keyExists(event, 'queryStringParameters', 'hostname'):
            return fail(Error("You have to pass 'hostname' querystring parameters."), raw)
        hostname: str = event['queryStringParameters']['hostname']

        if not keyExists(event, 'queryStringParameters', 'hash'):
            return fail(Error("You have to pass 'hash' querystring parameters."), raw)
        validationhash: str = event['queryStringParameters']['hash']

        if not keyExists(event, 'requestContext', 'identity', 'sourceIp'):
            return fail(Error("Source IP address cannot be extracted from request context."), raw)
        sourceip: str = event['requestContext']['identity']['sourceIp']

        internalip: str = ""
        if keyExists(event, 'queryStringParameters', 'internalip'):
            internalip = event['queryStringParameters']['internalip']

        sharedsecret: str = self.config.shared_secret(hostname)

        error = self.handler.checkhash(hostname, validationhash, sourceip, sharedsecret)
        if isinstance(error, Error):
            return fail(error, raw)

        result = error = self.handler.update(hostname, sourceip, internalip)
        if isinstance(error, Error):
            return fail(error, raw)

        return success(result, raw)
