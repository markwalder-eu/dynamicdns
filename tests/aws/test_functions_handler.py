import json
import unittest

from unittest.mock import (patch, MagicMock)

from dynamicdns.aws.functions.handler import handle 

from dynamicdns.aws.functions import (version, script, myip, dns)

class testHandler(unittest.TestCase):

    @patch('dynamicdns.aws.functions.version.handle') 
    @patch('dynamicdns.aws.functions.script.handle') 
    @patch('dynamicdns.aws.functions.myip.handle') 
    @patch('dynamicdns.aws.functions.dns.handle') 
    def testHandlerDNS(self, mock_dns: MagicMock, mock_myip: MagicMock, mock_script: MagicMock, mock_version: MagicMock):
        event = { 'resource':  '/dns', 'httpMethod': 'POST'}
        context = {}
        handle(event, context)
        mock_dns.assert_called_once_with(event, context)
        mock_myip.assert_not_called()
        mock_script.assert_not_called()
        mock_version.assert_not_called()

    @patch('dynamicdns.aws.functions.version.handle') 
    @patch('dynamicdns.aws.functions.script.handle') 
    @patch('dynamicdns.aws.functions.myip.handle') 
    @patch('dynamicdns.aws.functions.dns.handle') 
    def testHandlerMyIP(self, mock_dns: MagicMock, mock_myip: MagicMock, mock_script: MagicMock, mock_version: MagicMock):
        event = { 'resource':  '/myip', 'httpMethod': 'GET'}
        context = {}
        handle(event, context)
        mock_dns.assert_not_called()
        mock_myip.assert_called_once_with(event, context)
        mock_script.assert_not_called()
        mock_version.assert_not_called()

    @patch('dynamicdns.aws.functions.version.handle') 
    @patch('dynamicdns.aws.functions.script.handle') 
    @patch('dynamicdns.aws.functions.myip.handle') 
    @patch('dynamicdns.aws.functions.dns.handle') 
    def testHandlerScript(self, mock_dns: MagicMock, mock_myip: MagicMock, mock_script: MagicMock, mock_version: MagicMock):
        event = { 'resource':  '/script', 'httpMethod': 'GET'}
        context = {}
        handle(event, context)
        mock_dns.assert_not_called()
        mock_myip.assert_not_called()
        mock_script.assert_called_once_with(event, context)
        mock_version.assert_not_called()

    @patch('dynamicdns.aws.functions.version.handle') 
    @patch('dynamicdns.aws.functions.script.handle') 
    @patch('dynamicdns.aws.functions.myip.handle') 
    @patch('dynamicdns.aws.functions.dns.handle') 
    def testHandlerVersion(self, mock_dns: MagicMock, mock_myip: MagicMock, mock_script: MagicMock, mock_version: MagicMock):
        event = { 'resource':  '/version', 'httpMethod': 'GET'}
        context = {}
        handle(event, context)
        mock_dns.assert_not_called()
        mock_myip.assert_not_called()
        mock_script.assert_not_called()
        mock_version.assert_called_once_with(event, context)

    @patch('dynamicdns.aws.functions.version.handle') 
    @patch('dynamicdns.aws.functions.script.handle') 
    @patch('dynamicdns.aws.functions.myip.handle') 
    @patch('dynamicdns.aws.functions.dns.handle') 
    def testHandlerExecFail(self, mock_dns: MagicMock, mock_myip: MagicMock, mock_script: MagicMock, mock_version: MagicMock):
        event = { 'resource':  '/foo', 'httpMethod': 'GET'}
        context = {}
        handle(event, context)
        mock_dns.assert_not_called()
        mock_myip.assert_not_called()
        mock_script.assert_not_called()
        mock_version.assert_not_called()


if __name__ == '__main__':
    unittest.main()
