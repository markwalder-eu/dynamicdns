import json
import unittest

from unittest.mock import MagicMock, patch

import dynamicdns

from dynamicdns.aws.functions import __createAWSFunctions 

from dynamicdns.models import Error
from dynamicdns.aws.functions import (AWSFunctions, Route53Provider, S3ConfigProvider, Boto3Wrapper)
from dynamicdns.handler import Handler


class TestAWSFunctions(unittest.TestCase):


# -----------------------------------------------------------------------------
# VERSION
# -----------------------------------------------------------------------------

    
    def testVersion(self):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        event = {
            'queryStringParameters': {},
            'requestContext': {}
        } 
        context = {}

        result = self.functions.version(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ ' + 
            '"version": "' + dynamicdns.__version__ + '", ' + 
            '"author": "' + dynamicdns.__author__ + '", ' + 
            '"author-email": "' + dynamicdns.__author_email__ + '" ' +    
        '}')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.__createAWSFunctions') 
    def testVersionModuleFunctionSuccess(self, mocked_create):
        self.__setUpMocks(hashFailed = False, updateFailed = False)        
        mocked_create.return_value = self.functions

        result = dynamicdns.aws.functions.version({},{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads(
        '{' + 
            '"version": "' + dynamicdns.__version__ + '", ' + 
            '"author": "' + dynamicdns.__author__ + '", ' + 
            '"author-email": "' + dynamicdns.__author_email__ + '"' + 
        '}')
        self.assertEqual(a, b)


    @patch('dynamicdns.aws.functions.__createAWSFunctions') 
    def testVersionModuleFunctionFail(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        result = dynamicdns.aws.functions.version({},{})

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{"status": "FAIL", "message": "Error"}')
        self.assertEqual(a, b)

# -----------------------------------------------------------------------------
# INFO
# -----------------------------------------------------------------------------

    
    def testInfo(self):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        event = {
            'queryStringParameters': {},
            'requestContext': {}
        } 
        context = {}

        result = self.functions.info(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "SUCCESS", "message": { "queryStringParameters": {}, "requestContext": {} } }')
        self.assertEqual(a, b)


# -----------------------------------------------------------------------------
# LOCAL
# -----------------------------------------------------------------------------


    def testLocalRaw(self):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        event = {
            'queryStringParameters': { 'raw': '' },
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        } 
        context = {}

        result = self.functions.local(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')
        self.assertEqual(result['body'],'SUCCESS\n1.1.1.1')


    def testLocalJson(self):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        event = {
            'queryStringParameters': {},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        } 
        context = {}

        result = self.functions.local(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "SUCCESS", "message": "1.1.1.1" }')
        self.assertEqual(a, b)


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


    def testRemoteRaw(self):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        event = {
            'queryStringParameters': { 'raw': '', 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = self.functions.remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')
        self.assertEqual(result['body'],'SUCCESS\nOK')


    def testRemoteJson(self):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = self.functions.remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "SUCCESS", "message": "OK" }')
        self.assertEqual(a, b)


    def testRemoteMissingParamHostname(self):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        event = {
            'queryStringParameters': { 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        self.__remoteCaller(event, "You have to pass 'hostname' querystring parameters.")


    def testRemoteMissingParamHash(self):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        self.__remoteCaller(event, "You have to pass 'hash' querystring parameters.")


    def testRemoteMissingParamInternalIp(self):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = self.functions.remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "SUCCESS", "message": "OK" }')
        self.assertEqual(a, b)


    def testRemoteMissingParamSourceIp(self):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
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
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = self.functions.remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "FAIL", "message": "Hashcheck failed" }')
        self.assertEqual(a, b)


    def testRemoteUpdateFailed(self):
        self.__setUpMocks(hashFailed=False, updateFailed=True)
        event = {
            'queryStringParameters': { 'hostname': 'abc', 'hash': 'xyz', 'internalip': '2.2.2.2'},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        }
        context = {}
        
        result = self.functions.remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "FAIL", "message": "Update failed" }')
        self.assertEqual(a, b)


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

        result = self.functions.remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "FAIL", "message": "' + expMsg + '" }')
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()
