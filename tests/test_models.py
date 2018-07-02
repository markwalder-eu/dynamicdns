import unittest

from dynamicdns.models import ConfigProvider, DNSProvider

class TestModels(unittest.TestCase):
    
    def testConfigProvider(self):

        class ConfigProviderTest(ConfigProvider):
            pass
                
        config = ConfigProviderTest()

        self.assertRaises(NotImplementedError, config.load)
        self.assertRaises(NotImplementedError, config.shared_secret, 'abc')


    def testDNSProvider(self):

        class DNSProviderTest(DNSProvider):
            pass
        
        dns = DNSProviderTest()

        self.assertRaises(NotImplementedError, dns.read, 'abc')
        self.assertRaises(NotImplementedError, dns.update, 'abc', 'def')


if __name__ == '__main__':
    unittest.main()


