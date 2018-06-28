import json
import unittest

from unittest.mock import MagicMock

from dynamicdns.aws.functions import (AWSFunctions, Route53Provider, S3ConfigProvider)
from dynamicdns.handler import Handler


class TestAWSFunctionsInfo(unittest.TestCase):

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
    
    
    def testInfo(self):
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


if __name__ == '__main__':
    unittest.main()
