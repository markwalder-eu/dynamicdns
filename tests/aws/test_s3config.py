import unittest
import json

from unittest.mock import MagicMock, patch

from dynamicdns.models import ConfigProvider, Error
from dynamicdns.aws.boto3wrapper import Boto3Wrapper
from dynamicdns.aws.s3config import S3ConfigProvider


class TestS3ConfigProvider(unittest.TestCase):

    def testReadProps(self):
        config: S3ConfigProvider = self.__createConfigProvider(
        {   "hostname": {
                "aws_region": "region",
                "route_53_zone_id": "zone-id",
                "route_53_record_ttl": 42,
                "route_53_record_type": "record-type",
                "shared_secret": "shared-secret"
            }
        })

        with patch.dict('os.environ', {
            'CONFIG_S3_REGION': 'region',
            'CONFIG_S3_BUCKET': 'bucket',
            'CONFIG_S3_KEY': 'key',
        }):
            result = config.load()

            self.assertFalse(isinstance(result, Error))

            self.assertEqual(config.aws_region('hostname'), 'region')
            self.assertEqual(config.route_53_zone_id('hostname'), 'zone-id')
            self.assertEqual(config.route_53_record_ttl('hostname'), 42)
            self.assertEqual(config.route_53_record_type('hostname'), 'record-type')
            self.assertEqual(config.shared_secret('hostname'), 'shared-secret')


    def testMissingHostname(self):
        config: S3ConfigProvider = self.__createConfigProvider(
        {   "hostname": {
                "aws_region": "region",
                "route_53_zone_id": "zone-id",
                "route_53_record_ttl": 42,
                "route_53_record_type": "record-type",
                "shared_secret": "shared-secret"
            }
        })

        with patch.dict('os.environ', {
            'CONFIG_S3_REGION': 'region',
            'CONFIG_S3_BUCKET': 'bucket',
            'CONFIG_S3_KEY': 'key',
        }):
            result = config.load()

            self.assertFalse(isinstance(result, Error))
            with self.assertRaises(Exception):
                config.aws_region('hostname-not-in-config')


    def testMissingAttribute(self):
        config: S3ConfigProvider = self.__createConfigProvider(
        {   "hostname": {
                "route_53_zone_id": "zone-id",
                "route_53_record_ttl": 42,
                "route_53_record_type": "record-type",
                "shared_secret": "shared-secret"
            }
        })

        with patch.dict('os.environ', {
            'CONFIG_S3_REGION': 'region',
            'CONFIG_S3_BUCKET': 'bucket',
            'CONFIG_S3_KEY': 'key',
        }):
            result = config.load()

            self.assertFalse(isinstance(result, Error))
            with self.assertRaises(Exception):
                config.aws_region('hostname')

    def testReadException(self):
        config: S3ConfigProvider = self.__createConfigProvider(None, readException=True)

        with patch.dict('os.environ', {
            'CONFIG_S3_REGION': 'region',
            'CONFIG_S3_BUCKET': 'bucket',
            'CONFIG_S3_KEY': 'key',
        }):
            result = config.load()

            self.assertTrue(isinstance(result, Error))
            self.assertEqual(str(result), 'Could not read configuration. Excpeption: ReadException')


    def testMissingConfig(self):
        config: S3ConfigProvider = self.__createConfigProvider(None)

        self.__testWithMissingConfig(config, {
            'CONFIG_S3_BUCKET': 'bucket',
            'CONFIG_S3_KEY': 'key',
        })
        self.__testWithMissingConfig(config, {
            'CONFIG_S3_REGION': 'region',
            'CONFIG_S3_KEY': 'key',
        })
        self.__testWithMissingConfig(config, {
            'CONFIG_S3_REGION': 'region',
            'CONFIG_S3_BUCKET': 'bucket',
        })


    def __testWithMissingConfig(self, config, env_vars):
        with patch.dict('os.environ', env_vars):
            result = config.load()
            self.assertTrue(isinstance(result, Error))
            self.assertEqual(str(result), 'You have to configure the environment variables CONFIG_S3_REGION, CONFIG_S3_BUCKET and CONFIG_S3_KEY.')


    def __createConfigProvider(self, data, readException = False):
        boto3_wrapper: Boto3Wrapper = Boto3Wrapper()
        
        if readException:
            boto3_wrapper.client_get_object = MagicMock(side_effect=Exception('ReadException'))
        else:
            boto3_wrapper.client_get_object = MagicMock(return_value=json.dumps(data))
        
        boto3_wrapper.client_list_resource_record_sets = MagicMock(return_value=None)
        boto3_wrapper.client_change_resource_record_sets = MagicMock(return_value=None)

        return S3ConfigProvider(boto3_wrapper)
