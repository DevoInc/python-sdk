# Destination Email

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Destination Email](#destination-email)
  - [How to use](#how-to-use)
  - [Restrictions](#restrictions)
  - [Example](#example)
  - [Result](#result)
  - [Errors codes](#errors-codes)

<!-- /code_chunk_output -->

API have a email destination to send query results by email.

## How to use

As any query you must to add 'query', 'from' and 'to' date params. But It's not necessary add mode.type parameter because all response format will be csv. In a future will have support for more format, **if you need more format please request us**.

To use 'email' destination you must add destination parameter with type 'email' (see example).

- **Parameters:**

| Key | Type | Required | Description |
| --- | --- | --- | --- |
| email.to | string | Yes | Email target or email to send query results |
| email.subject | string | No | Email subject |
| retention.size | long | No | Max file size (kilobytes) before send mail. Default file retention was 5 MB |
| retention.time | long | No | Max time (seconds) before send mail. Default time was 15 mins |
| format | string | Optional | It's format of file compressed. (zip or gzip) by default zip |
| file.password | Optional | No | Add a password for file compressed. Only for zip format. |

## Restrictions

- The email target must be user of the domain.
- The file inner log format must be csv.
- The api was configure with a maximum (1 GB) and minimum (1 Mb) retention size, and it cannot be override by user.
- The api was configure with a maximum (24 hours) and minimum (5 mins) retention time, and it cannot be override by user.

## Example

```pyton
api = Client(auth={"key": "myapikey",
                   "secret": "myapisecret"},
             address="https://apiv2-eu.devo.com/search/query",
             config=ClientConfig(response="json", stream=False, processor=JSON,
                                 destination={
                                     "type": "email",
                                     "params": {
                                         "email.to": "user@devo.com",
                                         "email.subject": "Api v2 Test",
                                         "format": "gzip",
                                     },
                                 }))


response = api.query("from siem.logtrust.web.activity select * limit 10",
                     dates={"from": "yesterday()", "to": "now()"})

```

## Result

Send a email with a zip/gzip file with the results.

On query info:

```json
{
    "status": 0,
    "cid": "nhoSWU6ioj",
    "timestamp": 1541691126809,
    "object": {
        "status": "COMPLETED",
        "id": "bc2c33cd-b68c-4e5e-8e19-39e9cec29209",
        "eventGenerated": 81370,
        "eventsSent": 81370,
        "lastDatetime": 1541678102489,
        "extra": {
            "emailsSended": 8
        },
        "type": "email",
        "friendlyName": "email_YSx9daY9yC",
        "query": "from siem.logtrust.web.activity select *",
        "cid": "ghtufPRLQF",
        "owner": "5109b1ed2d9fb83885d90b5cad3c355c",
        "table": "siem.logtrust.web.activity",
        "domain": "self",
        "error": []
    }
}
```

On query Info with errors:

```json
{
    "status": 0,
    "cid": "BjQGorvYcO",
    "timestamp": 1541688414389,
    "object": {
        "status": "COMPLETED",
        "id": "b134e4ed-8f25-45e2-bc85-1d7c6756b522",
        "eventGenerated": 117589,
        "lastDatetime": 0,
        "extra": {
            "emailsSended": 0
        },
        "type": "email",
        "friendlyName": "email_pGfnGC630J",
        "query": "from siem.logtrust.web.activity select *",
        "cid": "vEBQl1YJJ7",
        "owner": "5109b1ed2d9fb83885d90b5cad3c355c",
        "table": "siem.logtrust.web.activity",
        "domain": "self",
        "error": [
            "Cannot send mail: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details. (Service: AmazonSimpleEmailService; Status Code: 403; Error Code: SignatureDoesNotMatch; Request ID: 367df816-e364-11e8-816d-a9462cc6a865)",
            "Cannot send mail: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details. (Service: AmazonSimpleEmailService; Status Code: 403; Error Code: SignatureDoesNotMatch; Request ID: 4622cb37-e364-11e8-a857-45d84765f497)",
            "Cannot send mail: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details. (Service: AmazonSimpleEmailService; Status Code: 403; Error Code: SignatureDoesNotMatch; Request ID: 4b053ffa-e364-11e8-85b7-9d27d154d9b7)",
            "Cannot send mail: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details. (Service: AmazonSimpleEmailService; Status Code: 403; Error Code: SignatureDoesNotMatch; Request ID: 4c4142af-e364-11e8-ad4d-ebbd0b2215e9)",
            "Cannot send mail: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details. (Service: AmazonSimpleEmailService; Status Code: 403; Error Code: SignatureDoesNotMatch; Request ID: 4d7fb600-e364-11e8-a12a-ef753fa5627c)",
            "Cannot send mail: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details. (Service: AmazonSimpleEmailService; Status Code: 403; Error Code: SignatureDoesNotMatch; Request ID: 4ed2e979-e364-11e8-936e-5dec0ebb792b)",
            "Cannot send mail: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details. (Service: AmazonSimpleEmailService; Status Code: 403; Error Code: SignatureDoesNotMatch; Request ID: 530a9fd8-e364-11e8-b0a2-11d6972bff3b)",
            "Cannot send mail: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details. (Service: AmazonSimpleEmailService; Status Code: 403; Error Code: SignatureDoesNotMatch; Request ID: 55178759-e364-11e8-a165-1bf81be3c086)"
        ]
    }
}
```

## Errors codes

```
## Errors

| Error Code | Message | Description |
|---|---|---|
| 213 | QUERY_EMAIL_BAD_SUBJECT |  Email subject must be a string or empty |
| 214 | QUERY_EMAIL_BAD_PARAMS_GZIP_PWD |  Send a file with format gzip cannot have password |
| 215 | QUERY_EMAIL_BAD_PARAMS_FORMAT |  File compress format must be zip or gzip |
| 216 | QUERY_EMAIL_NO_PARAMS |  Send by email needs parameters, at least email destination |
| 217 | QUERY_EMAIL_BAD_EMAIL_TO |  Email destination was invalid |
| 218 | QUERY_EMAIL_NO_DOMAIN_EMAIL_TO |  Email destination was not a member of domain |
| 219 | QUERY_EMAIL_BAD_SIZE_RETENTION |  Bad file size retention |
| 220 | QUERY_EMAIL_BAD_TIME_RETENTION |  Bad time retention |
| 221 | QUERY_EMAIL_BAD_FORMAT_PWD |  Bad format for file password |
| 222 | QUERY_EMAIL_DISABLED |  Destination email was disabled please contact us |
| 223 | QUERY_EMAIL_CREATE_FILE |  Cannot create temporal file to send by email |
| 224 | QUERY_EMAIL_SERVICE_INIT |  Cannot init email services |
| 225 | QUERY_EMAIL_ADD_CONTENT_FILE |  Cannot write in temporal file to upload to send email |
| 226 | QUERY_EMAIL_SEND_MAIL |  Cannot send email with events |
