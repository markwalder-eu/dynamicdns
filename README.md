
[![TravisCI](https://travis-ci.org/amarkwalder/dynamicdns.svg)](https://travis-ci.org/amarkwalder/dynamicdns)
[![codecov](https://codecov.io/gh/amarkwalder/dynamicdns/branch/master/graph/badge.svg)](https://codecov.io/gh/amarkwalder/dynamicdns)


# Dynamic DNS Utility

## Motiviation

Internet Service Providers allocate a dynamic IP address to a home router or modem. This makes it impossible to assign the IP address to a DNS name especially if the ISP changes the IP address which has been allocated earlier and the DNS name is not adapted accordingly after a change. Some of the home routers or modems support dynamic DNS clients, but most of them are bound to a paid service. Cloud services are not supported at all. All the cloud providers offer some kind of DNS functionality and a lot more features. Especially if you host your DNS domain on the cloud, it makes sense that your home address is maintained on the cloud as well.

Dynamic DNS Utility has been built to address the before mentioned gaps / features and bring dynamically updated IP addresses to cloud providers like AWS Route 53.

## Software Components

The Dynamic DNS Utility is mainly composed of two components:
* Client: Running locally in your home, scheduled to update the IP address in periodic intervalls   
* Server: Located in the cloud to update the home IP address on the cloud providers DNS service and serves as an access point for the client 

Security is implemented by using a shared secret known by the client and server, but is not transmitted over the wire. The client creates a hash over the parameters and sends this hash over the wire. The server does the same and compares the generated hash with the one transmitted over the wire. If both hashes are the same, the update is allowed. In addition the source IP address is part of the hash and therefore an additional security step is included in the update algorithm to compare the source IP address as well.

The client component is a shell script which can be scheduled locally to e.g. update the IP address all 5 minutes. The shell script can be downloaded from the server and executed. Therefore it is not required to install anything locally (except the required software components like curl, tail, head, ...). The configuration file can be omitted, but if you pass sensitive data like the shared secret in e.g. a cron job this sensitive data will be logged on the executing machine which could be a security breach if someone is able to access the logfiles. 

The server component is a lambda function which has been implemented with Python and Serverless. Configuration files are located in the cloud e.g. in case of AWS, the configuration file is located in a S3 bucket.

Currently only Amazon Web Services (AWS) is supported, but the architecture of the tool allows to support additional cloud providers like Azure, GCloud and any other which are supoorted by the Serverless framework.


# Installation

## Prerequisites 

* Install the serverless framework including the AWS credentials setup. For installation details see [Serverless - Quickstart](https://serverless.com/framework/docs/providers/aws/guide/quick-start/)
* Install `make` to easily create the configuration files and deploy the lambda function with serverless e.g. on Ubuntu run `sudo apt-get install make`


## AWS Setup

* Create on AWS Route 53 a new hosted zone (if you don't already have one you want to reuse) - [AWS Console - Route 53](https://console.aws.amazon.com/route53/home)
> Note: Remember the zone id of the created (or existing) Route 53 hosted zone for later use

* Create on AWS a new S3 Bucket (if you don't already have one you want to reuse) - [AWS Console - S3](https://console.aws.amazon.com/s3/home)
> Note: Remember the S3 bucket name of the created (or existing) S3 bucket for later use 

* Create on AWS a new certificate in certificate manager (if you don't already have one you want to reuse) - [AWS Console - Certificate Manager](https://console.aws.amazon.com/acm/home)
> Note: Remember the certificate name of the created (or existing) certificate for later use


## Create Configuration files and upload it to AWS S3 bucket

* Run `make create-config` to create the configuration files
> Note: You have to set the environment variables to include into the configuration files (see below for an example)

```
STAGE=dev \
URL=https://api-dev.domain.com \
API_DOMAIN_NAME=api-dev.domain.com \
API_DOMAIN_CERTIFICATE_NAME=*.domain.com \
DNS_HOSTNAME=home.dev.domain.com \
ROUTE53_ZONE_ID=1234 \
ROUTE53_RECORD_TTL=300 \
ROUTE53_RECORD_TYPE=A \
ROUTE53_REGION=us-east-1 \
S3_BUCKET=s3-bucket-name-dev \
S3_KEY=server-dev.config \
S3_REGION=us-east-1 \
SHARED_SECRET=secret \
\
make create-config
```

* Upload the `server-[STAGE].config` configuration file to the created S3 bucket.
> Note: The S3 bucket and S3 key has to be same as specified in the configuration file created before


## Deploy Dynamic DNS Lambda function and API Gateway to AWS

* Run `make deploy` to deploy the Lambda function and the API Gateway including the custom domain name 
> Note: The domain needs to be on Route53 that the custom domain name can be updated with the related host

```
STAGE=dev make deploy
```


## Test Dynamic DNS client

* Run `make run` to test the Dynamic DNS tool
> Note: It could take some time until the Lambda function and the API Gateway are deployed

```
STAGE=dev URL=https://api-dev.domain.com make run
```

* To install / run Dynamic DNS tool you could use the following command
> Note: The script depends on a few tools which have to be installed (grep, head, tail, awk, shasum, curl)

```
bash <(curl -sSL https://api-dev.domain.com/dynamicdns-v1/script) -c config/client-dev.config
```

# TODO
* Support fo additional cloud providers like Azure, GCloud, ...
* Windows Clients
* Dynamic DNS Protocol support to use the standard functions of routers and modems
