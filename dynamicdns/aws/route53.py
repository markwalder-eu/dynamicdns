
from dynamicdns.models import Error, ConfigProvider, DNSProvider
from dynamicdns.aws.s3config import S3ConfigProvider
from dynamicdns.aws.boto3wrapper import Boto3Wrapper


class Route53Provider(DNSProvider):

    def __init(self, boto3_wrapper: Boto3Wrapper, config: S3ConfigProvider):
        self.boto3_wrapper = boto3_wrapper
        self.config = config


    def read(self, hostname: str):
        try:
            recordset = self.boto3_wrapper.client_list_resource_record_sets(
                service_name = 'route53',
                region_name = self.config.aws_region(hostname),
                HostedZoneId = self.config.route_53_zone_id(hostname), 
                StartRecordName = hostname, 
                StartRecordType = self.config.route_53_record_type(hostname), 
                MaxItems = '2'
            )
            for record in recordset['ResourceRecordSets']:
                if record['Name'] == hostname or record['Name'] == hostname + ".":
                    if len(record['ResourceRecords']) == 1:
                        for subrecord in record['ResourceRecords']:
                            return subrecord['Value']                   
                    elif len(record['ResourceRecords']) > 1:
                        return Error('You should only have a single value for your dynamic record.  You currently have more than one.')
            return ""
        except:
            return Error("Retrieval of current ip address failed.")


    def update(self, hostname: str, updateip: str):
        try:
            self.boto3_wrapper.client_change_resource_record_sets(
                service_name = 'route53',
                region_name = self.config.aws_region(hostname),
                HostedZoneId = self.config.route_53_zone_id(hostname),
                ChangeBatch = {
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
        except Exception:
            return Error("Update of DNS record failed.")
