import json
import unittest

from unittest.mock import MagicMock, Mock, patch, mock_open

import dynamicdns

from dynamicdns.aws.functions import createAWSFunctions 

from dynamicdns.models import Error
from dynamicdns.aws.functions import (AWSFunctions, Route53Provider, S3ConfigProvider, Boto3Wrapper)
from dynamicdns.handler import Handler


class TestAWSFunctions(unittest.TestCase):


# -----------------------------------------------------------------------------
# AWS FUNCTIONS INIT
# -----------------------------------------------------------------------------


    @patch('dynamicdns.aws.functions.S3ConfigProvider.load') 
    def testAWSFunctionsInit(self, mocked_load):
        mocked_load.return_value = None

        result = dynamicdns.aws.functions.createAWSFunctions()

        self.assertFalse(isinstance(result, Error))


    @patch('dynamicdns.aws.functions.S3ConfigProvider.load') 
    def testAWSFunctionsInitFail(self, mocked_load):
        mocked_load.return_value = Error('Error')

        result = dynamicdns.aws.functions.createAWSFunctions()

        self.assertTrue(isinstance(result, Error))
        self.assertEqual(str(result), 'Error')


# -----------------------------------------------------------------------------
# VERSION
# -----------------------------------------------------------------------------

    
    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testVersion(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': {},
            'requestContext': {}
        } 
        context = {}

        result = dynamicdns.aws.functions.version(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ ' + 
            '"version": "' + dynamicdns.__version__ + '", ' + 
            '"author": "' + dynamicdns.__author__ + '", ' + 
            '"author-email": "' + dynamicdns.__author_email__ + '" ' +    
        '}')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testVersionModuleFunctionFailJson(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = dynamicdns.aws.functions.version({},{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{"status": "FAIL", "message": "Error"}')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testVersionModuleFunctionFailRaw(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = dynamicdns.aws.functions.version({ 'queryStringParameters': { 'raw': ''} },{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')        
        self.assertEqual(result['body'], 'FAIL\nError')


# -----------------------------------------------------------------------------
# INFO
# -----------------------------------------------------------------------------

    
    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testInfo(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': {},
            'requestContext': {}
        } 
        context = {}

        result = dynamicdns.aws.functions.info(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "SUCCESS", "message": { "queryStringParameters": {}, "requestContext": {} } }')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testInfoModuleFunctionFailJson(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = dynamicdns.aws.functions.info({},{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{"status": "FAIL", "message": "Error"}')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testInfoModuleFunctionFailRaw(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = dynamicdns.aws.functions.info({ 'queryStringParameters': { 'raw': ''} },{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')        
        self.assertEqual(result['body'], 'FAIL\nError')


# -----------------------------------------------------------------------------
# LOCAL
# -----------------------------------------------------------------------------


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testLocalRaw(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'raw': '' },
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        } 
        context = {}

        result = dynamicdns.aws.functions.local(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')
        self.assertEqual(result['body'],'SUCCESS\n1.1.1.1')


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testLocalJson(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': {},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        } 
        context = {}

        result = dynamicdns.aws.functions.local(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "SUCCESS", "message": "1.1.1.1" }')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testLocalModuleFunctionFailJson(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = dynamicdns.aws.functions.local({},{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{"status": "FAIL", "message": "Error"}')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testLocalModuleFunctionFailRaw(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = dynamicdns.aws.functions.local({ 'queryStringParameters': { 'raw': ''} },{})

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
# REMOTE
# -----------------------------------------------------------------------------


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testRemoteRaw(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = dynamicdns.aws.functions.remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')
        self.assertEqual(result['body'],'SUCCESS\nOK')


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testRemoteJson(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = dynamicdns.aws.functions.remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "SUCCESS", "message": "OK" }')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testRemoteModuleFunctionFailJson(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = dynamicdns.aws.functions.remote({},{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{"status": "FAIL", "message": "Error"}')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testRemoteModuleFunctionFailRaw(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = dynamicdns.aws.functions.remote({ 'queryStringParameters': { 'raw': ''} },{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')        
        self.assertEqual(result['body'], 'FAIL\nError')

    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testRemoteMissingParamInternalIp(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = dynamicdns.aws.functions.remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')

        a = json.loads(result['body'])
        b = json.loads('{ "status": "SUCCESS", "message": "OK" }')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testRemoteMissingParamHostname(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        self.__remoteCaller(event, "You have to pass 'hostname' querystring parameters.")


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testRemoteMissingParamHash(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        self.__remoteCaller(event, "You have to pass 'hash' querystring parameters.")


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
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
# SCRIPT
# -----------------------------------------------------------------------------

    
    @patch('dynamicdns.aws.functions.createAWSFunctions')
    def testScript(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': {},
            'requestContext': {}
        } 
        context = {}

        with patch('builtins.open', mock_open(read_data='SCRIPT')):
            result = dynamicdns.aws.functions.script(event, context)
        
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')
        self.assertEqual(result['body'], 'SCRIPT')


    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testScriptModuleFunctionFailJson(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        with patch('builtins.open', mock_open(read_data='SCRIPT')):
            result = dynamicdns.aws.functions.script({},{})
        
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')        

        a = json.loads(result['body'])
        b = json.loads('{ "status": "FAIL", "message": "Error" }')
        self.assertEqual(a, b)

    @patch('dynamicdns.aws.functions.createAWSFunctions') 
    def testScriptModuleFunctionFailRaw(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        with patch('builtins.open', mock_open(read_data='SCRIPT')):
            result = dynamicdns.aws.functions.script({ 'queryStringParameters': { 'raw': ''} },{})
        
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')        
        self.assertEqual(result['body'], 'FAIL\nError')


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


    def __remoteCaller(self, event, expMsg):
        context = {}

        result = dynamicdns.aws.functions.remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "FAIL", "message": "' + expMsg + '" }')
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()
