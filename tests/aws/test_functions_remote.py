import unittest
import json

from unittest.mock import MagicMock

from dynamicdns.aws.functions import AWSFunctions, S3ConfigProvider, Route53Provider
from dynamicdns.handler import Handler
from dynamicdns.models import Error


class TestAWSFunctionsRemote(unittest.TestCase):

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


    def __setUpMocks(self, hashFailed: bool, updateFailed: bool):
        config = S3ConfigProvider(None)
        config.aws_region = MagicMock(return_value='aws_region')
        config.route_53_record_ttl = MagicMock(return_value='route_53_record_ttl')
        config.route_53_record_type = MagicMock(return_value='route_53_record_type')
        config.route_53_zone_id = MagicMock(return_value='route_53_zone_id')
        config.shared_secret = MagicMock(return_value='shared_secret')

        dns = Route53Provider()
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

        result = self.functions.remote(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "FAIL", "message": "' + expMsg + '" }')
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()


