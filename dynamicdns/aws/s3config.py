import json
import os

from dynamicdns.models import Error, ConfigProvider
from dynamicdns.aws.boto3wrapper import Boto3Wrapper

class S3ConfigProvider(ConfigProvider):

    def load(self):
        config_s3_region: str = os.environ['CONFIG_S3_REGION']
        config_s3_bucket: str = os.environ['CONFIG_S3_BUCKET']
        config_s3_key: str = os.environ['CONFIG_S3_KEY']

        if not ('CONFIG_S3_REGION' in os.environ 
            and 'CONFIG_S3_BUCKET' in os.environ 
            and 'CONFIG_S3_KEY' in os.environ):
            return Error("You have to configure the environment variables CONFIG_S3_REGION, CONFIG_S3_BUCKET and CONFIG_S3_KEY.")

        try:
            s3 = Boto3Wrapper.get_client('s3', config_s3_region)    
            data = s3.get_object(Bucket=config_s3_bucket, Key=config_s3_key)
            self.config = json.loads(data['Body'].read())
        except Exception:
            return Error("Could not read configuration.")
        
    def aws_region(self, hostname: str):
        return self.__checkAndReturn(hostname, 'aws_region')

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
            raise "Configuration for hostname '" + hostname + "' and attribute '" +  attr+ "' not found."            
        return self.config[hostname][attr]
