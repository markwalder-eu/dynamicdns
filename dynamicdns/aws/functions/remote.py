import os
import json

from dynamicdns.models import Error, ConfigProvider, DNSProvider
from dynamicdns.handler import Handler
from dynamicdns.util import success, fail, keyExists

from dynamicdns.aws.boto3wrapper import Boto3Wrapper
from dynamicdns.aws.s3config import S3ConfigProvider
from dynamicdns.aws.route53 import Route53Provider


def remote(event, context):
    
    # Create AWS Functions Object  
    fn = error = createAWSFunctions()
    if isinstance(error, Error):
        raw: bool = keyExists(event, 'queryStringParameters', 'raw')
        return fail(error, raw)

    # Extract Raw Parameter 
    raw: bool = keyExists(event, 'queryStringParameters', 'raw')

    # Extract Hostname Parameter  
    if not keyExists(event, 'queryStringParameters', 'hostname'):
        return fail(Error("You have to pass 'hostname' querystring parameters."), raw)
    hostname: str = event['queryStringParameters']['hostname']

    # Extract Validation Hash Parameter 
    if not keyExists(event, 'queryStringParameters', 'hash'):
        return fail(Error("You have to pass 'hash' querystring parameters."), raw)
    validationhash: str = event['queryStringParameters']['hash']

    # Extract Source IP Parameter 
    if not keyExists(event, 'requestContext', 'identity', 'sourceIp'):
        return fail(Error("Source IP address cannot be extracted from request context."), raw)
    sourceip: str = event['requestContext']['identity']['sourceIp']

    # Extract Internal IP Parameter (if present) 
    internalip: str = ""
    if keyExists(event, 'queryStringParameters', 'internalip'):
        internalip = event['queryStringParameters']['internalip']

    # Execute Remote Function 
    result = error= fn.remote(hostname, validationhash, sourceip, internalip, raw)
    if isinstance(error, Error):
        return fail(str(error), raw)
    return success(result, raw)
 
 
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


    def remote(self, hostname, validationhash, sourceip, internalip, raw):

        sharedsecret: str = self.config.shared_secret(hostname)

        error = self.handler.checkhash(hostname, validationhash, sourceip, sharedsecret)
        if isinstance(error, Error):
            return error

        result = error = self.handler.update(hostname, sourceip, internalip)
        if isinstance(error, Error):
            return error

        return result
