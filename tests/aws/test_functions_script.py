import json
import unittest

from unittest.mock import MagicMock, Mock, patch, mock_open

from dynamicdns.aws.functions.script import (createAWSFunctions, AWSFunctions, script) 

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
# SCRIPT
# -----------------------------------------------------------------------------

    
    @patch('dynamicdns.aws.functions.script.createAWSFunctions')
    def testScript(self, mocked_create):
        self.__setUpMocks(hashFailed=False, updateFailed=False)
        mocked_create.return_value = self.functions
        event = {
            'queryStringParameters': {},
            'requestContext': {}
        } 
        context = {}

        with patch('builtins.open', mock_open(read_data='SCRIPT')):
            result = script(event, context)
        
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')
        self.assertEqual(result['body'], 'SCRIPT')


    @patch('dynamicdns.aws.functions.script.createAWSFunctions') 
    def testScriptModuleFunctionFailJson(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        with patch('builtins.open', mock_open(read_data='SCRIPT')):
            result = script({},{})
        
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')        

        a = json.loads(result['body'])
        b = json.loads('{ "status": "FAIL", "message": "Error" }')
        self.assertEqual(a, b)

    @patch('dynamicdns.aws.functions.script.createAWSFunctions') 
    def testScriptModuleFunctionFailRaw(self, mocked_create):
        mocked_create.return_value = Error('Error')
        
        with patch('builtins.open', mock_open(read_data='SCRIPT')):
            result = script({ 'queryStringParameters': { 'raw': ''} },{})
        
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


if __name__ == '__main__':
    unittest.main()
