import os
import json

from dynamicdns.models import Error, ConfigProvider, DNSProvider
from dynamicdns.processor import Processor
from dynamicdns.util import success, fail, keyExists

import dynamicdns

from dynamicdns.aws import (s3config, route53, boto3wrapper)

from dynamicdns.aws.boto3wrapper import Boto3Wrapper
from dynamicdns.aws.s3config import S3ConfigProvider
from dynamicdns.aws.route53 import Route53Provider


def handle(event, context):
    
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

    # Boto3 Wrapper - Utility for reading / writing AWS objects
    boto3_wrapper: Boto3Wrapper = boto3wrapper.factory()

    # S3 Configuration - Read settings from a S3 bucket
    config: ConfigProvider = s3config.factory(boto3_wrapper)
    error = config.load()
    if isinstance(error, Error):
        return fail(str(error), raw)
    
    # Route 53 - Read / write DNS entry 
    dns: DNSProvider = route53.factory(boto3_wrapper, config)
    processor = dynamicdns.processor.factory(dns)

    # Get shared secret from S3 bucket 
    sharedsecret: str = config.shared_secret(hostname)

    # Check passed hash value 
    error = processor.checkhash(hostname, validationhash, sourceip, sharedsecret)
    if isinstance(error, Error):
        return fail(str(error), raw)

    # Update entry on Route 53 
    result = error = processor.update(hostname, sourceip, internalip)
    if isinstance(error, Error):
        return fail(str(error), raw)

    # Return status success 
    return success(result, raw)
