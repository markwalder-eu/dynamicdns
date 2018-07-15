import os
import json

import dynamicdns

from dynamicdns.models import Error, ConfigProvider, DNSProvider
from dynamicdns.handler import Handler
from dynamicdns.util import success, fail, keyExists

from dynamicdns.aws.boto3wrapper import Boto3Wrapper
from dynamicdns.aws.s3config import S3ConfigProvider
from dynamicdns.aws.route53 import Route53Provider


def info(event, context):
    fn = error = createAWSFunctions()
    if isinstance(error, Error):
        raw: bool = keyExists(event, 'queryStringParameters', 'raw')
        return fail(error, raw)
    return fn.info(event, context)


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


    def info(self, event, context):
        return success(event, False)