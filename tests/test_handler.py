import unittest

from dynamicdns.aws.s3config import S3ConfigProvider
from dynamicdns.aws.route53 import Route53Provider
from dynamicdns.models import Error
from dynamicdns.handler import Handler

from unittest.mock import MagicMock

import hashlib

class TestHandler(unittest.TestCase):
    
    def testCheckhash(self):
        self.__setUpMocks(None, None)

        hostname = "host.domain.com"
        validationhash = "f5f9b9b2f166aa50e3bba3200857ed9fbfc1feccdc7ac2fce9796e55cba82cda"
        sourceip = "1.1.1.1"
        sharedsecret = "1234567890"

        result = self.handler.checkhash(hostname, validationhash, sourceip, sharedsecret)

        self.assertFalse(isinstance(result, Error))


    def testCheckhashWrongFormat(self):
        self.__setUpMocks(None, None)

        hostname = "host.domain.com"
        validationhash = "This is a wrong format of a validation hash"
        sourceip = "1.1.1.1"
        sharedsecret = "1234567890"

        result = self.handler.checkhash(hostname, validationhash, sourceip, sharedsecret)

        self.assertTrue(isinstance(result, Error))
        self.assertEqual(str(result), "You must pass a valid sha256 hash in the hash= querystring parameter.")


    def testCheckhashWrongValidation(self):
        self.__setUpMocks(None, None)

        hostname = "host.domain.com"
        validationhash = "f5f9b9b2f166aa50e3bba3200857ed9fbfc1feccdc7ac2fce9796e55cba8ffff"
        sourceip = "1.1.1.1"
        sharedsecret = "1234567890"

        result = self.handler.checkhash(hostname, validationhash, sourceip, sharedsecret)

        self.assertTrue(isinstance(result, Error))
        self.assertEqual(str(result), "Validation of hashes failed.")


    def testUpdateCurrentEqualsUpdate(self):
        self.__setUpMocks("1.1.1.1", None)

        hostname = "host.domain.com"
        sourceip = "1.1.1.1"
        internalip = ""
        
        result = self.handler.update(hostname, sourceip, internalip)

        self.assertEqual(str(result), "Your IP '1.1.1.1' address matches the current DNS record for 'host.domain.com'.")


    def testUpdateCurrentNotEqualsUpdate(self):
        self.__setUpMocks("2.2.2.2", "1.1.1.1")

        hostname = "host.domain.com"
        sourceip = "1.1.1.1"
        internalip = ""
        
        result = self.handler.update(hostname, sourceip, internalip)

        self.assertEqual(str(result), "Your hostname record 'host.domain.com' has been updated from '2.2.2.2' to '1.1.1.1'.")


    def testUpdateUpdateReadFailed(self):
        self.__setUpMocks(Error("Read failed"), None)

        hostname = "host.domain.com"
        sourceip = "1.1.1.1"
        internalip = ""
        
        result = self.handler.update(hostname, sourceip, internalip)

        self.assertTrue(isinstance(result, Error))
        self.assertEqual(str(result), "Read failed")


    def testUpdateUpdateWriteFailed(self):
        self.__setUpMocks("2.2.2.2", Error("Write failed"))

        hostname = "host.domain.com"
        sourceip = "1.1.1.1"
        internalip = ""
        
        result = self.handler.update(hostname, sourceip, internalip)

        self.assertTrue(isinstance(result, Error))
        self.assertEqual(str(result), "Write failed")

    def testUpdateWithInternalIp(self):
        self.__setUpMocks("2.2.2.2", "3.3.3.3")

        hostname = "host.domain.com"
        sourceip = "1.1.1.1"
        internalip = "3.3.3.3"
        
        result = self.handler.update(hostname, sourceip, internalip)

        self.assertEqual(str(result), "Your hostname record 'host.domain.com' has been updated from '2.2.2.2' to '3.3.3.3'.")


    def __setUpMocks(self, readReturnValue, updateReturnValue):
        dns = Route53Provider(None, None)
        dns.read = MagicMock(return_value=readReturnValue)
        dns.update = MagicMock(return_value=updateReturnValue)
        
        self.handler = Handler(dns)


if __name__ == '__main__':
    unittest.main()


