from __future__ import print_function

import json
import re
import hashlib
import boto3
import os

class Error:
    def __init__(self, msg):
        self.msg = msg
 
    def __str__(self):
        return str(self.msg)
 
def info(event, context):
    return success(event, event)

def local(event, context):
    return success(event['requestContext']['identity']['sourceIp'], event)

def remote(event, context):

    error = checkparameters(event)
    if isinstance(error, Error):
        return fail(error, event)

    config_s3_region = os.environ['CONFIG_S3_REGION']
    config_s3_bucket = os.environ['CONFIG_S3_BUCKET']
    config_s3_key = os.environ['CONFIG_S3_KEY']

    hostname = event['queryStringParameters']['hostname']
    validationhash = event['queryStringParameters']['hash']
    sourceip = event['requestContext']['identity']['sourceIp'] 
    internalip = ""
    updateip = sourceip
    if event['queryStringParameters'] and 'internalip' in event['queryStringParameters']:
        internalip = event['queryStringParameters']['internalip']
        updateip = internalip

    error = checkhashformat(validationhash)
    if isinstance(error, Error):
        return fail(error, event)

    config = error = readconfig(hostname, config_s3_region, config_s3_bucket, config_s3_key)
    if isinstance(error, Error):
        return fail(error, event)

    region = config[hostname]['aws_region']
    zoneid = config[hostname]['route_53_zone_id']
    recordttl = config[hostname]['route_53_record_ttl']
    recordtype = config[hostname]['route_53_record_type']
    sharedsecret = config[hostname]['shared_secret']

    error = comparehash(sourceip, hostname, sharedsecret, validationhash)
    if isinstance(error, Error):
        return fail(error, event)

    currentip = error = readroute53(region, zoneid, hostname, recordtype)
    if isinstance(error, Error):
        return fail(error, event)

    if currentip == updateip:
        return success("Your IP address matches the current Route53 DNS record.", event)
        
    updateroute53(region, zoneid, hostname, recordtype, recordttl, updateip)
    return success("Your hostname record '" + hostname + "' has been set to '" + updateip + "'.", event)

def success(message, event):
    raw = checkraw(event)
    if raw:
        headers = {
            "Content-Type": "text/plain"
        }
        body = "SUCCESS\n" + message
        response = {
            "statusCode": 200,
            "headers": headers,
            "body": body
        }
    else:
        headers = {
                "Content-Type": "application/json"
        }
        body = {
            "status": "SUCCESS",
            "message": message
        }
        response = {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(body)
        }
    return response

def fail(error, event):
    raw = checkraw(event)
    if raw:
        headers = {
            "Content-Type": "text/plain"
        }
        body = "FAIL\n" + str(error)
        response = {
            "statusCode": 200,
            "headers": headers,
            "body": body
        }
    else:
        headers = {
                "Content-Type": "application/json"
        }
        body = {
            "status": "FAIL",
            "message": str(error)
        }
        response = {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(body)
        }
    return response

def checkraw(event):
    return event['queryStringParameters'] and 'raw' in event['queryStringParameters']

def checkparameters(event):
    if not (event['queryStringParameters'] 
        and 'hostname' in event['queryStringParameters'] 
        and 'hash' in event['queryStringParameters']):
        return Error("You have to pass hostname= and hash= as querystring parameters. The querystring parameter internalip= is optional.")
    if not (os.environ 
        and 'CONFIG_S3_REGION' in os.environ 
        and 'CONFIG_S3_BUCKET' in os.environ 
        and 'CONFIG_S3_KEY' in os.environ):
        return Error("You have to configure the environment variables CONFIG_S3_REGION, CONFIG_S3_BUCKET and CONFIG_S3_KEY.")

def checkhashformat(validationhash):
    if not re.match(r'[0-9a-fA-F]{64}', validationhash):
        return Error("You must pass a valid sha256 hash in the hash= querystring parameter.")

def readconfig(hostname, config_s3_region, config_s3_bucket, config_s3_key):
    try:
        s3 = boto3.client('s3', config_s3_region)    
        data = s3.get_object(Bucket=config_s3_bucket, Key=config_s3_key)
        config = json.loads(data['Body'].read())
    except Exception as ex:
        return Error("Could not read configuration. Exception: " + str(ex))
    if not config \
        or not hostname in config \
        or not 'aws_region' in config[hostname] \
        or not 'route_53_zone_id' in config[hostname] \
        or not 'route_53_record_ttl' in config[hostname] \
        or not 'route_53_record_type' in config[hostname] \
        or not 'shared_secret' in config[hostname]:
        return Error("Configuration for hostname '" + hostname + "' or configuration values not found.")
    return config

def comparehash(sourceip, hostname, sharedsecret, validationhash):
    hashinput = sourceip + hostname + sharedsecret
    calculatedhash = hashlib.sha256(hashinput.encode('utf-8')).hexdigest()
    if not calculatedhash == validationhash:
        return Error("Validation of hashes failed.")

def readroute53(region, zoneid, hostname, recordtype):
    client = boto3.client('route53', region_name=region)
    recordset = client.list_resource_record_sets(
        HostedZoneId=zoneid, 
        StartRecordName=hostname, 
        StartRecordType=recordtype, 
        MaxItems='2'
    )
    for record in recordset['ResourceRecordSets']:
        if record['Name'] == hostname or record['Name'] == hostname + ".":
            if len(record['ResourceRecords']) == 1:
                for subrecord in record['ResourceRecords']:
                    return subrecord['Value']                   
            elif len(eachRecord['ResourceRecords']) > 1:
                return Error('You should only have a single value for your dynamic record.  You currently have more than one.')
    return ""

def updateroute53(region, zoneid, hostname, recordtype, recordttl, updateip):
    client = boto3.client('route53', region_name=region)
    client.change_resource_record_sets(
        HostedZoneId=zoneid,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': hostname,
                        'Type': recordtype,
                        'TTL': recordttl,
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
