import unittest

from unittest.mock import patch, mock_open

from dynamicdns.aws.functions.script import script 


class TestAWSFunctions(unittest.TestCase):

    
    def testScript(self):
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


if __name__ == '__main__':
    unittest.main()
