import json
import unittest

from dynamicdns.aws.functions.local import (local) 


class TestAWSFunctions(unittest.TestCase):


    def testLocal(self):

        event = {
            'queryStringParameters': { 'raw': '' },
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        } 
        context = {}

        result = local(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')
        self.assertEqual(result['body'],'SUCCESS\n1.1.1.1')


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


    def testLocalMissingParamSourceIp(self):
        event = { 'queryStringParameters': { 'raw': '' } } 
        self.__localCaller(event, True)
        event = {} 
        self.__localCaller(event, False)

        event = { 'queryStringParameters': { 'raw': '' }, 'requestContext': {} } 
        self.__localCaller(event, True)
        event = { 'requestContext': {} } 
        self.__localCaller(event, False)

        event = { 'queryStringParameters': { 'raw': '' }, 'requestContext': None } 
        self.__localCaller(event, True)
        event = { 'requestContext': None } 
        self.__localCaller(event, False)

        event = { 'queryStringParameters': { 'raw': '' }, 'requestContext': { 'identity': {} } } 
        self.__localCaller(event, True)
        event = { 'requestContext': { 'identity': {} } } 
        self.__localCaller(event, False)

        event = { 'queryStringParameters': { 'raw': '' }, 'requestContext': { 'identity': None } } 
        self.__localCaller(event, True)
        event = { 'queryStringParameters': {}, 'requestContext': { 'identity': None } }
        self.__localCaller(event, False)


# -----------------------------------------------------------------------------
# TESTING HELPER METHODS
# -----------------------------------------------------------------------------


    def __localCaller(self, event, raw):
        context = {}

        result = local(event, context)

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
