import json
import boto3


class Boto3Wrapper():
    
    def client_get_object(self, *args, **kwargs):
        client = boto3.client(*args, **kwargs)
        return client.get_object(*args, **kwargs)

    def client_list_resource_record_sets(self, *args, **kwargs):
        client = boto3.client(self, *args, **kwargs)
        return client.list_resource_record_sets(self, *args, **kwargs)

    def client_change_resource_record_sets(self, *args, **kwargs):
        client = boto3.client(self, *args, **kwargs)
        return client.change_resource_record_sets(self, *args, **kwargs)
