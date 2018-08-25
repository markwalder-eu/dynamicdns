import json
import os

from dynamicdns.models import Error, ConfigProvider
from dynamicdns.aws.boto3wrapper import Boto3Wrapper


def factory(boto3_wrapper: Boto3Wrapper):
    return S3ConfigProvider(boto3_wrapper)


class S3ConfigProvider(ConfigProvider):

    def __init__(self, boto3_wrapper: Boto3Wrapper):
        self.boto3_wrapper = boto3_wrapper 

    def load(self):
        if not ('CONFIG_S3_REGION' in os.environ 
            and 'CONFIG_S3_BUCKET' in os.environ 
            and 'CONFIG_S3_KEY' in os.environ):
            return Error("You have to configure the environment variables CONFIG_S3_REGION, CONFIG_S3_BUCKET and CONFIG_S3_KEY.")

        config_s3_region: str = os.environ['CONFIG_S3_REGION']
        config_s3_bucket: str = os.environ['CONFIG_S3_BUCKET']
        config_s3_key: str = os.environ['CONFIG_S3_KEY']

        try:
            data = self.boto3_wrapper.client_get_object(
                region=config_s3_region, 
                bucket=config_s3_bucket,
                key=config_s3_key
            )
            self.config = json.loads(data)
        except Exception as ex:
            return Error("Could not read configuration. Excpeption: " + str(ex))
        
    def route_53_region(self, hostname: str):
        return self.__checkAndReturn(hostname, 'route_53_region')

    def route_53_zone_id(self, hostname: str):
        return self.__checkAndReturn(hostname, 'route_53_zone_id')

    def route_53_record_ttl(self, hostname: str):
        return self.__checkAndReturn(hostname, 'route_53_record_ttl')

    def route_53_record_type(self, hostname: str):
        return self.__checkAndReturn(hostname, 'route_53_record_type')

    def shared_secret(self, hostname: str):
        return self.__checkAndReturn(hostname, 'shared_secret')

    def __checkAndReturn(self, hostname: str, attr: str):
        if not hostname in self.config or not attr in self.config[hostname]:
            raise Exception("Configuration for hostname '" + hostname + "' and attribute '" +  attr+ "' not found.")
        return self.config[hostname][attr]
