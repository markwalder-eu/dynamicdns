import unittest
import json

from dynamicdns.aws.functions import AWSFunctions, S3ConfigProvider, Route53Provider
from dynamicdns.handler import Handler

from unittest.mock import MagicMock

class TestAWSFunctionsLocal(unittest.TestCase):

    def setUp(self):
        config = S3ConfigProvider()
        config.aws_region = MagicMock(return_value='aws_region')
        config.route_53_record_ttl = MagicMock(return_value='route_53_record_ttl')
        config.route_53_record_type = MagicMock(return_value='route_53_record_type')
        config.route_53_zone_id = MagicMock(return_value='route_53_zone_id')
        config.shared_secret = MagicMock(return_value='shared_secret')

        dns = Route53Provider(config)
        dns.read = MagicMock(return_value="1.1.1.1")
        dns.update = MagicMock(return_value=None)
        
        handler = Handler(dns)
        handler.checkhash = MagicMock(return_value=None)
        handler.update = MagicMock(return_value="OK")

        self.functions = AWSFunctions(config, dns, handler)
    
    def testLocalRaw(self):
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
        event = {} 
        self.__localCaller(event)

        event = { 'requestContext': {} } 
        self.__localCaller(event)

        event = { 'requestContext': { 'identity': {} } } 
        self.__localCaller(event)

        event = { 'queryStringParameters': {}, 'requestContext': { 'identity': {} } }
        self.__localCaller(event)


    def __localCaller(self, event):
        context = {}

        result = self.functions.local(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "FAIL", "message": "Source IP address cannot be extracted from request context." }')
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()


