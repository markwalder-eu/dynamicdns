import json
import unittest

from unittest.mock import MagicMock, Mock, patch, mock_open

from dynamicdns.aws.functions.local import (createAWSFunctions, AWSFunctions, local) 

from dynamicdns.models import Error

from dynamicdns.aws.route53 import Route53Provider
from dynamicdns.aws.s3config import S3ConfigProvider
from dynamicdns.aws.boto3wrapper import Boto3Wrapper

from dynamicdns.handler import Handler


class TestAWSFunctions(unittest.TestCase):


# -----------------------------------------------------------------------------
# AWS FUNCTIONS INIT
# -----------------------------------------------------------------------------


    @patch('dynamicdns.aws.s3config.S3ConfigProvider.load') 
    def testAWSFunctionsInit(self, mocked_load):
        mocked_load.return_value = None

        result = createAWSFunctions()

        self.assertFalse(isinstance(result, Error))


    @patch('dynamicdns.aws.s3config.S3ConfigProvider.load') 
    def testAWSFunctionsInitFail(self, mocked_load):
        mocked_load.return_value = Error('Error')

        result = createAWSFunctions()

        self.assertTrue(isinstance(result, Error))
        self.assertEqual(str(result), 'Error')


# -----------------------------------------------------------------------------
# LOCAL
# -----------------------------------------------------------------------------


    @patch('dynamicdns.aws.functions.local.createAWSFunctions') 
    def testLocalRaw(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'raw': '' },
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        } 
        context = {}

        result = local(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')
        self.assertEqual(result['body'],'SUCCESS\n1.1.1.1')


    @patch('dynamicdns.aws.functions.local.createAWSFunctions') 
    def testLocalJson(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': {},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        } 
        context = {}

        result = local(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "SUCCESS", "message": "1.1.1.1" }')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.local.createAWSFunctions') 
    def testLocalModuleFunctionFailJson(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = local({},{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{"status": "FAIL", "message": "Error"}')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.local.createAWSFunctions') 
    def testLocalModuleFunctionFailRaw(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = local({ 'queryStringParameters': { 'raw': ''} },{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')        
        self.assertEqual(result['body'], 'FAIL\nError')


    def testLocalMissingParamSourceIp(self):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        event = { 'queryStringParameters': { 'raw': '' } } 
        self.__localCaller(event, True)

        event = {} 
        self.__localCaller(event, False)

        event = { 'requestContext': {} } 
        self.__localCaller(event, False)

        event = { 'requestContext': None } 
        self.__localCaller(event, False)

        event = { 'requestContext': { 'identity': {} } } 
        self.__localCaller(event, False)

        event = { 'queryStringParameters': {}, 'requestContext': { 'identity': {} } }
        self.__localCaller(event, False)


# -----------------------------------------------------------------------------
# TESTING HELPER METHODS
# -----------------------------------------------------------------------------


    def __setUpMocks(self, hashFailed: bool, updateFailed: bool):
        config = S3ConfigProvider(None)
        config.aws_region = MagicMock(return_value='aws_region')
        config.route_53_record_ttl = MagicMock(return_value='route_53_record_ttl')
        config.route_53_record_type = MagicMock(return_value='route_53_record_type')
        config.route_53_zone_id = MagicMock(return_value='route_53_zone_id')
        config.shared_secret = MagicMock(return_value='shared_secret')

        dns = Route53Provider(None, None)
        dns.read = MagicMock(return_value="1.1.1.1")
        dns.update = MagicMock(return_value=None)
        
        handler = Handler(dns)
        if hashFailed:
            handler.checkhash = MagicMock(return_value=Error("Hashcheck failed"))
        else:
            handler.checkhash = MagicMock(return_value=None)
        
        if updateFailed:
            handler.update = MagicMock(return_value=Error("Update failed"))
        else:
            handler.update = MagicMock(return_value="OK")

        self.functions = AWSFunctions(config, dns, handler)


    def __localCaller(self, event, raw):
        context = {}

        result = self.functions.local(event, context)

        if raw:
            self.assertEqual(result['statusCode'], 200)
            self.assertEqual(result['headers']['Content-Type'], 'text/plain')
            self.assertEqual(result['body'],'FAIL\nSource IP address cannot be extracted from request context.')
        else:
            self.assertEqual(result['statusCode'], 200)
            self.assertEqual(result['headers']['Content-Type'], 'application/json')
            
            a = json.loads(result['body'])
            b = json.loads('{ "status": "FAIL", "message": "Source IP address cannot be extracted from request context." }')
            self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()
