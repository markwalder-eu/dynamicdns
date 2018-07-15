import unittest

from unittest.mock import patch, mock_open

from dynamicdns.aws.functions.script import handle 


class TestScript(unittest.TestCase):

    
    def testScript(self):
        event = {
            'queryStringParameters': {},
            'requestContext': {}
        } 
        context = {}

        with patch('builtins.open', mock_open(read_data='SCRIPT')):
            result = handle(event, context)
        
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['headers']['Content-Type'], 'text/plain')
        self.assertEqual(result['body'], 'SCRIPT')


if __name__ == '__main__':
    unittest.main()
