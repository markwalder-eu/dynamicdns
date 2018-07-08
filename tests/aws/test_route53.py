import unittest
from unittest.mock import MagicMock

from dynamicdns.models import DNSProvider, Error
from dynamicdns.aws.boto3wrapper import Boto3Wrapper
from dynamicdns.aws.s3config import S3ConfigProvider
from dynamicdns.aws.route53 import Route53Provider


class TestRoute53Provider(unittest.TestCase):

    def testReadHostnameWithoutDot(self):
        dns = self.__createDNSProvider(
        { 'ResourceRecordSets':
        [
            { 'Name': 'test', 'ResourceRecords':
                [ 
                    { 'Value': 'test-value' }
                ]
            }
        ]})

        result = error = dns.read('test')

        self.assertFalse(isinstance(error, Error))
        self.assertEqual(result, 'test-value')

    def testReadHostnameWithDot(self):
        dns = self.__createDNSProvider(
        { 'ResourceRecordSets':
        [
            { 'Name': 'test.', 'ResourceRecords':
                [ 
                    { 'Value': 'test-value' }
                ]
            }
        ]})

        result = error = dns.read('test')

        self.assertFalse(isinstance(error, Error))
        self.assertEqual(result, 'test-value')

    def testReadMultipleValues(self):
        dns = self.__createDNSProvider(
        { 'ResourceRecordSets':
        [
            { 'Name': 'test', 'ResourceRecords':
                [ 
                    { 'Value': 'test-value-1' },
                    { 'Value': 'test-value-2' }
                ]
            }
        ]})

        result = error = dns.read('test')

        self.assertTrue(isinstance(error, Error))
        self.assertEqual(str(result), 'You should only have a single value for your dynamic record. You currently have more than one.')

    def testReadNotFound(self):
        dns = self.__createDNSProvider(
        { 'ResourceRecordSets':
        [
            { 'Name': 'test-new', 'ResourceRecords':
                [ 
                    { 'Value': 'test-value' }
                ]
            }
        ]})

        result = error = dns.read('test')

        self.assertFalse(isinstance(error, Error))
        self.assertEqual(result, '')

    def testReadEmpty1(self):
        dns = self.__createDNSProvider({'ResourceRecordSets':[]})

        result = error = dns.read('test')

        self.assertFalse(isinstance(error, Error))
        self.assertEqual(result, '')

    def testReadEmpty2(self):
        dns = self.__createDNSProvider({})
        
        result = error = dns.read('test')

        self.assertTrue(isinstance(error, Error))
        self.assertEqual(str(result), 'Retrieval of current ip address failed. Excpeption: \'ResourceRecordSets\'')

    def testReadException(self):
        dns = self.__createDNSProvider({}, readException = True)
        
        result = error = dns.read('test')

        self.assertTrue(isinstance(error, Error))
        self.assertEqual(str(result), 'Retrieval of current ip address failed. Excpeption: ReadException')

    def testUpdate(self):
        dns = self.__createDNSProvider({})
        
        result = error = dns.update('test', '1.1.1.1')

        self.assertFalse(isinstance(error, Error))
        self.assertEqual(result, '1.1.1.1')

    def testUpdateException(self):
        dns = self.__createDNSProvider(data = {}, updateException = True)
        
        result = error = dns.update('test', '1.1.1.1')

        self.assertTrue(isinstance(error, Error))
        self.assertEqual(str(result), 'Update of DNS record failed. Exception: UpdateException')

    def __createDNSProvider(self, data, readException = False, updateException = False):
        boto3_wrapper: Boto3Wrapper = Boto3Wrapper()
        boto3_wrapper.client_get_object = MagicMock(return_value=None)
        
        if readException:
            boto3_wrapper.client_list_resource_record_sets = MagicMock(side_effect=Exception('ReadException'))
        else:
            boto3_wrapper.client_list_resource_record_sets = MagicMock(return_value=data)
        
        if updateException:
            boto3_wrapper.client_change_resource_record_sets = MagicMock(side_effect=Exception('UpdateException'))
        else:
            boto3_wrapper.client_change_resource_record_sets = MagicMock(return_value=None)

        config: S3ConfigProvider = S3ConfigProvider(None)
        config.aws_region = MagicMock(return_value='aws_region')
        config.route_53_record_ttl = MagicMock(return_value='route_53_record_ttl')
        config.route_53_record_type = MagicMock(return_value='route_53_record_type')
        config.route_53_zone_id = MagicMock(return_value='route_53_zone_id')
        config.shared_secret = MagicMock(return_value='shared_secret')

        return Route53Provider(boto3_wrapper, config)
