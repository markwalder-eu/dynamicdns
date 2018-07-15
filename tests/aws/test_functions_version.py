import json
import unittest

import dynamicdns

from dynamicdns.aws.functions.version import version 


class TestAWSFunctions(unittest.TestCase):

    
    def testVersion(self):
        event = {
            'queryStringParameters': {},
            'requestContext': {}
        } 
        context = {}

        result = version(event, context)

        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'application/json')
        
        a = json.loads(result['body'])
        b = json.loads('{ ' + 
            '"version": "' + dynamicdns.__version__ + '", ' + 
            '"author": "' + dynamicdns.__author__ + '", ' + 
            '"author-email": "' + dynamicdns.__author_email__ + '" ' +    
        '}')
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()
