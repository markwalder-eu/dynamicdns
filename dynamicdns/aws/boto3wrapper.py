import json
import boto3


class Boto3Wrapper():
    
    def client_get_object(self, region, bucket, key):
        client = boto3.client(service_name='s3',region_name=region)
        data = client.get_object(Bucket=bucket, Key=key)
        return data['Body'].read().decode('utf-8')

    def client_list_resource_record_sets(self, region, hosted_zone_id, start_record_name, start_record_type, max_items):
        client = boto3.client(service_name='route53', region_name=region)
        return client.list_resource_record_sets(HostedZoneId = hosted_zone_id, StartRecordName = start_record_name, StartRecordType = start_record_type, MaxItems = max_items)

    def client_change_resource_record_sets(self, region, hosted_zone_id, change_batch):
        client = boto3.client(service_name='route53',region_name=region)
        return client.change_resource_record_sets(HostedZoneId = hosted_zone_id, ChangeBatch = change_batch)
