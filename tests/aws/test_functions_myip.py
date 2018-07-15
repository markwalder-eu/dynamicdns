import json
import unittest

from dynamicdns.aws.functions.myip import handle 


class testMyIP(unittest.TestCase):


    def testMyIP(self):

        event = {
            'queryStringParameters': { 'raw': '' },
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        } 
        context = {}

        result = handle(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')
        self.assertEqual(result['body'],'SUCCESS\n1.1.1.1')


        event = {
            'queryStringParameters': {},
            'requestContext': { 'identity': { 'sourceIp': '1.1.1.1' } }
        } 
        context = {}

        result = handle(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ "status": "SUCCESS", "message": "1.1.1.1" }')
        self.assertEqual(a, b)


    def testMyIPMissingParamSourceIp(self):
        event = { 'queryStringParameters': { 'raw': '' } } 
        self.__myIPCaller(event, True)
        event = {} 
        self.__myIPCaller(event, False)

        event = { 'queryStringParameters': { 'raw': '' }, 'requestContext': {} } 
        self.__myIPCaller(event, True)
        event = { 'requestContext': {} } 
        self.__myIPCaller(event, False)

        event = { 'queryStringParameters': { 'raw': '' }, 'requestContext': None } 
        self.__myIPCaller(event, True)
        event = { 'requestContext': None } 
        self.__myIPCaller(event, False)

        event = { 'queryStringParameters': { 'raw': '' }, 'requestContext': { 'identity': {} } } 
        self.__myIPCaller(event, True)
        event = { 'requestContext': { 'identity': {} } } 
        self.__myIPCaller(event, False)

        event = { 'queryStringParameters': { 'raw': '' }, 'requestContext': { 'identity': None } } 
        self.__myIPCaller(event, True)
        event = { 'queryStringParameters': {}, 'requestContext': { 'identity': None } }
        self.__myIPCaller(event, False)


# -----------------------------------------------------------------------------
# TESTING HELPER METHODS
# -----------------------------------------------------------------------------


    def __myIPCaller(self, event, raw):
        context = {}

        result = handle(event, context)

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
