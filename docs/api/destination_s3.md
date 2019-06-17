# Destination S3

API have a S3 destination to send query results to S3.

## How to use

As any query you must to add 'query', 'from' and 'to' date params. But It's not necessary add mode.type parameter because all response format will be csv. In a future will have support for more format, **if you need more format please request us**.
To use 's3' destination you must add destination parameter with type 's3' (see example).

- **Parameters:**

| Key | Type | Required | Description |
| --- | --- | --- | --- |
| aws.bucket | string | No*, nice to have | AWS bucket name. By default uses a enviroment.properties/s3-delivery.properties value with the same key.  |
| aws.region | string | No*, nice to have | AWS region. [Regions](https://docs.aws.amazon.com/es_es/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-available-regions)  |
| aws.accesskey | string | No*, nice to have | AWS access key credential |
| aws.secretkey | string | No*, nice to have | AWS access password credential |
| format | string | Optional | It's format of file compressed. (zip or gzip) by default zip |
| file.password | Optional | No | Add a password for file compressed. Only for zip format. |



*If the user not set any AWS config by default uses enviroment.properties/s3-delivery.properties configuration. But if aws.bucket was set all AWS config must be set. It's highly recommendable set an user s3 configuration.

## Example

```python
from devo.api import Client

api = Client(key="myapikey",
              secret="myapisecret",
              url="https://apiv2-eu.devo.com/search/query",
              user="user@devo.com",
              app_name="testing app")
              
              
response = api.query("from siem.logtrust.web.activity select *", 
                     dates={"from":"yesterday()", "to": "now()"}, 
                     destination= { 
                     "type":"email",
                     "params":{
                            "aws.bucket": "blu-2223",
                            "aws.region": "eu-west-1",
                            "aws.accesskey": "AKI*************",
                            "aws.secretkey": "T********/**********15tpn3***V2UZ",
                            "format": "zip"
                        },
                     })
```

## Results

All the queries results will be upload to aws bucket in one or many files depends for the size of the results. 

The max file size of file can be configured using the propertie ``aws.file.size``, by default was 500 Mbs.

The files will be upload with this format:

```bash
apiv2_<task id>_<index>.csv.(zip|gz)
```
Examples:

```bash
apiv2_983c5a6b-7081-40eb-a631-7492d9badbfe_001.csv.zip
apiv2_983c5a6b-7081-40eb-a631-7492d9badbfe_002.csv.zip
apiv2_983c5a6b-7081-40eb-a631-7492d9badbfe_003.csv.zip
apiv2_983c5a6b-7081-40eb-a631-7492d9badbfe_004.csv.zip

apiv2_4c92c89e-19a3-4e49-bb8a-4dbf30d47214_001.csv.gz
apiv2_4c92c89e-19a3-4e49-bb8a-4dbf30d47214_002.csv.gz
```

If you want to see the paths of upload files you can query the task status to see the current upload files (task aren't finished) or see all files paths (finished task).

Example:

```json
{
    "status": 0,
    "cid": "tjIqEhbIKZ",
    "timestamp": 1533548393561,
    "object": {
        "status": "COMPLETED",
        "id": "983c5a6b-7081-40eb-a631-7492d9badbfe",
        "eventGenerated": 2619588,
        "eventsSent": 2619588,
        "lastDatetime": 0,
        "extra": {
            "paths": [
                "https://sis-2523.s3.eu-west-1.amazonaws.com/apiv2_983c5a6b-7081-40eb-a631-7492d9badbfe_001.csv.zip",
                "https://sis-2523.s3.eu-west-1.amazonaws.com/apiv2_983c5a6b-7081-40eb-a631-7492d9badbfe_002.csv.zip",
                "https://sis-2523.s3.eu-west-1.amazonaws.com/apiv2_983c5a6b-7081-40eb-a631-7492d9badbfe_003.csv.zip",
                "https://sis-2523.s3.eu-west-1.amazonaws.com/apiv2_983c5a6b-7081-40eb-a631-7492d9badbfe_004.csv.zip"
            ]
        },
        "type": "s3",
        "friendlyName": "s3_ezilvjQ1Sh",
        "query": "from siem.logtrust.web.activity select *",
        "cid": "lSypa1lvKv",
        "owner": "kW5Ule1m*omUatc8tu4S5LuQSnX9UpLs",
        "table": "siem.logtrust.web.activity",
        "error": []
    }
}
```

## Configuration
All the configuration was in ``s3-delivery.properties`` and some values was ``environment.properties`` :

| Key | Type | Description |
|---|---|---|
| aws.accesskey | string | Aws configuration by default, access key. |
| aws.secretkey | string | Aws configuration by default, secret/pwd key. |
| aws.bucketName | string | Aws configuration by default, bucket name. |
| aws.region | string | Aws configuration by default, aws region. |
| s3Delivery.tmp.dir | string | Temporal path to create files after upload then |
| s3Delivery.tmp.clean | boolean | Clean tmp directory at api startup |
| aws.file.size | long | Max file size for s3 files in bytes. The file can be overload size for a little bytes to avoid split a event in 2 files |

## Errors

| Error Code | Message | Description |
|---|---|---|
| 200 | S3 credentials cannot be empty or blank  | Please validate the destination credentials, because something was not send. |
| 201 | Cannot create S3 client | Something was wrong when aws was created. |
| 202 | Cannot upload file to s3 bucket | Something was wrong on upload file to s3 bucket. |
| 203 | Cannot create temporal file to upload to s3 bucket | Cannot create temporal file to zip query response. Please validate temporal directory configuration. |
| 204 | Cannot write in temporal file to upload to s3 bucket | Cannot add info to temporal file, please validate temporal directory configuration or disk free space. |
| 205 | S3 upload must have all bucket info (bucket name, acccess key, access pwd and region | Verified if all aws parameters was setted. |
| 206 | Bucket parameter must be string and it cannot be empty | Bucket name parameter must be string |
| 207 | Access key parameter must be string and it cannot be empty | Access key parameter must be string |
| 208 | Password key parameter must be string and it cannot be empty | Password/secret key parameter must be string |
| 209 | Region parameter must be string and it cannot be empty | Region parameter must be string |
| 210 | File compress format must be zip or gzip | File compress format must be zip or gzip |
| 211 | S3 upload with format gzip cannot have password | Only zip format can be password |
| 212 | File compress pwd format string and it cannot be empty | Password parameter must be string |

## AWS S3 upload methods

AWS SDK had 2 methods to upload files to s3:

- *Multipart upload:* It's for files bigger than 5mbs, this method uses a multipart upload with a concurrent threads 
to obtain a faster upload. [Limits of multipart upload](https://docs.aws.amazon.com/es_es/AmazonS3/latest/dev/qfacts.html)
- *Simple upload files:* It's for upload small files.

