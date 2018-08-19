
from dynamicdns.models import Error, ConfigProvider, DNSProvider
from dynamicdns.aws.s3config import S3ConfigProvider
from dynamicdns.aws.boto3wrapper import Boto3Wrapper


def factory(boto3_wrapper: Boto3Wrapper, config: ConfigProvider):
    return Route53Provider(boto3_wrapper, config)


class Route53Provider(DNSProvider):

    def __init__(self, boto3_wrapper: Boto3Wrapper, config: S3ConfigProvider):
        self.boto3_wrapper = boto3_wrapper
        self.config = config


    def read(self, hostname: str):
        try:
            recordset = self.boto3_wrapper.client_list_resource_record_sets(
                region = self.config.aws_region(hostname),
                hosted_zone_id = self.config.route_53_zone_id(hostname), 
                start_record_name = hostname, 
                start_record_type = self.config.route_53_record_type(hostname), 
                max_items = '2'
            )
            for record in recordset['ResourceRecordSets']:
                if record['Name'] == hostname or record['Name'] == hostname + ".":
                    if len(record['ResourceRecords']) != 1:
                        return Error('You should only have a single value for your dynamic record. You currently have more than one.')
                    return record['ResourceRecords'][0]['Value']
            return ""
        except Exception as ex:
            return Error("Retrieval of current ip address failed. Excpeption: " + str(ex))


    def update(self, hostname: str, updateip: str):
        try:
            self.boto3_wrapper.client_change_resource_record_sets(
                region = self.config.aws_region(hostname),
                hosted_zone_id = self.config.route_53_zone_id(hostname),
                change_batch = {
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': hostname,
                                'Type': self.config.route_53_record_type(hostname),
                                'TTL': self.config.route_53_record_ttl(hostname),
                                'ResourceRecords': [
                                    {
                                        'Value': updateip
                                    }
                                ]
                            }
                        }
                    ]
                }
            )
            return updateip
        except Exception as ex:
            return Error("Update of DNS record failed. Exception: " + str(ex))
