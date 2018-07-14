import os
import json

import dynamicdns

from dynamicdns.models import Error, ConfigProvider, DNSProvider
from dynamicdns.handler import Handler
from dynamicdns.util import success, fail, keyExists

from dynamicdns.aws.boto3wrapper import Boto3Wrapper
from dynamicdns.aws.s3config import S3ConfigProvider
from dynamicdns.aws.route53 import Route53Provider


def version(event, context):
    fn = error = createAWSFunctions()
    if isinstance(error, Error):
        raw: bool = keyExists(event, 'queryStringParameters', 'raw')
        return fail(error, raw)
    return fn.version(event, context)


def info(event, context):
    fn = error = createAWSFunctions()
    if isinstance(error, Error):
        raw: bool = keyExists(event, 'queryStringParameters', 'raw')
        return fail(error, raw)
    return fn.info(event, context)


def local(event, context):
    fn = error = createAWSFunctions()
    if isinstance(error, Error):
        raw: bool = keyExists(event, 'queryStringParameters', 'raw')
        return fail(error, raw)
    return fn.local(event, context)


def remote(event, context):
    fn = error = createAWSFunctions()
    if isinstance(error, Error):
        raw: bool = keyExists(event, 'queryStringParameters', 'raw')
        return fail(error, raw)

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

    result = error= fn.remote(hostname, validationhash, sourceip, internalip, raw)
    if isinstance(error, Error):
        return fail(str(error), raw)
    return success(result, raw)


def script(event, context):
    fn = error = createAWSFunctions()
    if isinstance(error, Error):
        raw: bool = keyExists(event, 'queryStringParameters', 'raw')
        return fail(error, raw)
    return fn.script(event, context)
 
 
def createAWSFunctions():
    boto3_wrapper = Boto3Wrapper()
    config: ConfigProvider = S3ConfigProvider(boto3_wrapper)
    error = config.load()
    if isinstance(error, Error):
        return error
    dns: DNSProvider = Route53Provider(boto3_wrapper, config)
    handler: Handler = Handler(dns)
    return AWSFunctions(config, dns, handler)


class AWSFunctions:

    def __init__(self, config: ConfigProvider, dns: DNSProvider, handler: Handler):
        self.config = config
        self.dns = dns
        self.handler = handler


    def version(self, event, context):
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


    def info(self, event, context):
        return success(event, False)


    def local(self, event, context):
        
        raw: bool = keyExists(event, 'queryStringParameters', 'raw')
        
        if not keyExists(event, 'requestContext', 'identity', 'sourceIp'):
            return fail(Error("Source IP address cannot be extracted from request context."), raw)
        
        sourceip: str = event['requestContext']['identity']['sourceIp']
        
        return success(sourceip, raw)


    def remote(self, hostname, validationhash, sourceip, internalip, raw):

        sharedsecret: str = self.config.shared_secret(hostname)

        error = self.handler.checkhash(hostname, validationhash, sourceip, sharedsecret)
        if isinstance(error, Error):
            return error

        result = error = self.handler.update(hostname, sourceip, internalip)
        if isinstance(error, Error):
            return error

        return result


    def script(self, event, context):
        file = open("dynamicdns/scripts/dynamic-dns-client", "r") 
        content = file.read()
        file.close()

        headers = {
            "Content-Type": "text/plain"
        }
        body = content
        response = {
            "statusCode": 200,
            "headers": headers,
            "body": body
        }
        return response