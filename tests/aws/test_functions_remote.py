import json
import unittest

from unittest.mock import MagicMock, Mock, patch, mock_open

from dynamicdns.aws.functions.remote import (createAWSFunctions, AWSFunctions, remote) 

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
# REMOTE
# -----------------------------------------------------------------------------


    @patch('dynamicdns.aws.functions.remote.createAWSFunctions') 
    def testRemoteRaw(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')
        self.assertEqual(result['body'],'SUCCESS\nOK')


    @patch('dynamicdns.aws.functions.remote.createAWSFunctions') 
    def testRemoteJson(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "SUCCESS", "message": "OK" }')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.remote.createAWSFunctions') 
    def testRemoteModuleFunctionFailJson(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = remote({},{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{"status": "FAIL", "message": "Error"}')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.remote.createAWSFunctions') 
    def testRemoteModuleFunctionFailRaw(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = remote({ 'queryStringParameters': { 'raw': ''} },{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')        
        self.assertEqual(result['body'], 'FAIL\nError')


    @patch('dynamicdns.aws.functions.remote.createAWSFunctions') 
    def testRemoteModuleFunctionCallFailJson(self, mocked_create):
        self.__setUpMocks(hashFailed=True, updateFailed=False)
        mocked_create.return_value = self.functions
        
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}

        result = remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{"status": "FAIL", "message": "Hashcheck failed"}')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.remote.createAWSFunctions') 
    def testRemoteModuleFunctionCallFailRaw(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=True)
        mocked_create.return_value = self.functions
        
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2', 'raw': ''},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}

        result = remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')        
        self.assertEqual(result['body'], 'FAIL\nUpdate failed')


    @patch('dynamicdns.aws.functions.remote.createAWSFunctions') 
    def testRemoteMissingParamInternalIp(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')

        a = json.loads(result['body'])
        b = json.loads('{ "status": "SUCCESS", "message": "OK" }')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.remote.createAWSFunctions') 
    def testRemoteMissingParamHostname(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        self.__remoteCaller(event, "You have to pass 'hostname' querystring parameters.")


    @patch('dynamicdns.aws.functions.remote.createAWSFunctions') 
    def testRemoteMissingParamHash(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        self.__remoteCaller(event, "You have to pass 'hash' querystring parameters.")


    @patch('dynamicdns.aws.functions.remote.createAWSFunctions') 
    def testRemoteMissingParamSourceIp(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'}
        }
        self.__remoteCaller(event, "Source IP address cannot be extracted from request context.")

        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': {}
        }
        self.__remoteCaller(event, "Source IP address cannot be extracted from request context.")

        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': None
        }
        self.__remoteCaller(event, "Source IP address cannot be extracted from request context.")

        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': {} } 
        }
        self.__remoteCaller(event, "Source IP address cannot be extracted from request context.")


    def testRemoteHashcheckFailed(self):
        self.__setUpMocks(hashFailed=True, updateFailed=False)

        result = self.functions.remote('abc', 'xyz','1.1.1.1', '2.2.2.2', False)

        self.assertTrue(isinstance(result, Error))
        self.assertEqual(str(result), "Hashcheck failed")


    def testRemoteUpdateFailed(self):
        self.__setUpMocks(hashFailed=False, updateFailed=True)
        
        result = self.functions.remote('abc', 'xyz', '1.1.1.1', '2.2.2.2', False)

        self.assertTrue(isinstance(result, Error))
        self.assertEqual(str(result), "Update failed")


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


    def __remoteCaller(self, event, expMsg):
        context = {}

        result = remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "FAIL", "message": "' + expMsg + '" }')
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()
