import boto3

from dynamicdns.models import Error, ConfigProvider, DNSProvider

from dynamicdns.aws.s3config import S3ConfigProvider


class Route53Provider(DNSProvider): # pragma: no cover

    def __init(self, config: S3ConfigProvider):
        super().__init__(config)


    def read(self, hostname: str):
        try:
            client = boto3.client('route53', region_name = self.config.aws_region(hostname))
            recordset = client.list_resource_record_sets(
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
                        raise 'You should only have a single value for your dynamic record.  You currently have more than one.'
            return ""
        except:
            return Error("Retrieval of current ip address failed.")


    def update(self, hostname: str, updateip: str):
        try:
            client = boto3.client('route53', region_name = self.config.aws_region(hostname))
            client.change_resource_record_sets(
                HostedZoneId = self.config.route_53_zone_id(hostname),
                ChangeBatch={
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
