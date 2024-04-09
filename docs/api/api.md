# Devo API (Client)

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Devo API (Client)](#devo-api-client)
  - [Overview](#overview)
  - [Endpoints](#endpoints)
    - [API](#api)
      - [Differences in use from version 2 to 3](#differences-in-use-from-version-2-to-3)
      - [Differences in use from version 3 to 4](#differences-in-use-from-version-3-to-4)
  - [USAGE](#usage)
    - [Constructor](#constructor)
    - [ClientConfig](#clientconfig)
    - [query() params](#query-params)
    - [Result returned](#result-returned)
      - [Non stream call](#non-stream-call)
      - [Stream call](#stream-call)
  - [Not verify certificates](#not-verify-certificates)
  - [Use custom CA to verify](#use-custom-ca-to-verify)
  - [Processors flags](#processors-flags)
    - [Flag list](#flag-list)
      - [DEFAULT example in Python 3, response csv](#default-example-in-python-3-response-csv)
      - [DEFAULT example in Python 2.7, response csv](#default-example-in-python-27-response-csv)
      - [TO_STR example in Python 3, response csv](#to_str-example-in-python-3-response-csv)
      - [TO_BYTES example in Python 2.7, response csv](#to_bytes-example-in-python-27-response-csv)
      - [SIMPLECOMPACT_TO_ARRAY example in Python 3, response json/simple/compact](#simplecompact_to_array-example-in-python-3-response-jsonsimplecompact)
      - [SIMPLECOMPACT_TO_OBJ example in Python 3, response json/simple/compact](#simplecompact_to_obj-example-in-python-3-response-jsonsimplecompact)
  - [The "from" and "to", formats and other stuff](#the-from-and-to-formats-and-other-stuff)
    - [Date Formats](#date-formats)
    - [____***Dates***](#____dates)
    - [____***Days***](#____days)
    - [____***Hours***](#____hours)
    - [Retries](#retries)
    - [Keep Alive mechanism support](#keep-alive-mechanism-support)
  - [CLI USAGE](#cli-usage)
  - [Choosing Format](#choosing-format)
    - [Response type JSON](#response-type-json)
    - [Response type json/compact](#response-type-jsoncompact)
    - [Response type json/simple](#response-type-jsonsimple)
    - [Response type json/simple/compact](#response-type-jsonsimplecompact)
    - [Response type msgpack](#response-type-msgpack)
    - [Response type csv](#response-type-csv)
    - [Response type tsv](#response-type-tsv)
  - [Exceptions and Errors](#exceptions-and-errors)

<!-- /code_chunk_output -->

## Overview

This library performs queries to the Client API (Search rest api) of Devo.

## Endpoints

### API

To perform a request with API, first choose the required endpoint depending on the region your are accessing from:

| Region  | Endpoint                                |
|-------- |---------------------------------------- |
| USA     | <https://apiv2-us.devo.com/search/query>  |
| Canada  | <https://apiv2-ca.devo.com/search/query>  |
| Europe  | <https://apiv2-eu.devo.com/search/query>  |
| Spain   | <https://apiv2-es.devo.com/search/query>  |
| APAC   | <https://api-apac.devo.com/search/query>  |

You have more information in the official documentation of Devo, [REST API](https://docs.devo.com/space/latest/95128275/Query%20API).

#### Differences in use from version 2 to 3

You have a special README to quickly show the important changes suffered from version 2 to 3

[You can go read it here](api_v3_changes.md)

#### Differences in use from version 3 to 4

You have a special README to quickly show the important changes suffered from version 3 to 4

[You can go read it here](api_v4_changes.md)

## USAGE

### Constructor

- address: endpoint
- auth: object with auth params (key and secret, token or jwt)
  - key: The key of the domain
  - secret: The secret of the domain
  - token: Auth token
  - jwt: JWT token
- retries: number of retries for connection errors in a query (`0`, no retry by default)
- timeout: timeout of socket (`300` seconds by default)
- retry_delay: retry delay value in seconds (`5` seconds by default). This is the base delay for the Exponential backoff algorithm with rate reduction of `2`
- config: dict or ClientConfig object
- verify: whether enable or disable the TLS authentication of endpoint (`True` by default). **DEVO will always provide a secure endpoint for ALL its services**. Disable at your own risk.

```python
from devo.api import Client

api = Client(auth= {"key":"myapikey", "secret":"myapisecret"}, 
             address="https://apiv2-eu.devo.com/search/query")


api = Client(auth={"token":"myauthtoken"},
             address="https://apiv2-eu.devo.com/search/query")

api = Client(auth={"jwt":"myauthtoken"},
             address="https://apiv2-eu.devo.com/search/query")
```

### ClientConfig

- processor: processor for response, default is None
- response: format of response
- destination: Destination options, see Documentation for more info
- stream: Stream queries or not
- pragmas: pragmas por query: {"user": "Username", "app_name": "app name", "comment": "This query is for x"}
  - All pragmas are optional
- keepAliveToken: KeepAlive token for long responses queries, see specific Section in this document for more info

```python
from devo.api import Client, ClientConfig

config = ClientConfig(response="json", pragmas={"user": "jose_ramon_id153"})

api = Client(auth= {"key":"myapikey", "secret":"myapisecret"}, 
             address="https://apiv2-eu.devo.com/search/query",
             config=config)


config = ClientConfig(response="json/compact", stream=False,
                      pragmas={"user": "jose_ramon_id153", "app_name": "devo-sdk-tests-master"})

api = Client(auth= {"key":"myapikey", "secret":"myapisecret"}, 
             address="https://apiv2-eu.devo.com/search/query",
             config=config)
```  

### query() params

`def query(self, **kwargs)`

- query: Query to perform
- query_id: Query ID to perform the query
- dates: Dict with "from" and "to" keys for date rangue, and "timeZone" for define timezone, if you want
- limit: Max number of rows
- offset: start of needle for query
- comment: comment for query pragmas
- Result of the query (dict) or Iterator object

### Result returned

Client support streaming of responses

* When the stream mode is enabled, the response is asynchronously available for the code using the Client, as the server is returning it. Therefore, there is no need to wait for the whole response to start processing it. It is also quite useful for query running online with no ending or ending expecting in the future. As the data is available we can be working with it.
* When the stream mode is not enabled, we have to wait for the query response to be completed and returned by server.  

Depending on the `stream` mode enabled in `ClientConfig`:

| Response mode       | Stream mode enabled | Stream mode not enabled |
|---------------------|---------------------|-------------------------|
| json                | *Not supported*     | `str`                   |
| json/compact        | *Not supported*     | `str`                   |
| json/simple         | `Iterator[str]`     | `str`                   |
| json/simple/compact | `Iterator[str]`     | `str`                   |
| msgpack             | *Not supported*     | `bytes`                 |
| csv                 | `Iterator[str]`     | `str`                   |
| tsv                 | `Iterator[str]`     | `str`                   |
| xls                 | *Not supported*     | `bytes`                 |

#### Non stream call

- Result of the query in str/bytes when query work
- JSON Object when query has errors
- You can use all the response formats in non-stream mode.

#### Stream call

- Generator with result of the query, str, when query work
- JSON Object when query has errors
- Stream available response formats:
  - json/simple
  - json/simple/compact
  - csv (comma separated values)
  - tsv (tabulator separated Values)

Normal/Non stream response:

```python
from devo.api import Client, ClientConfig

api = Client(auth={"key":"myapikey", "secret": "myapisecret"},
             address="https://apiv2-eu.devo.com/search/query", 
             config=ClientConfig(response="json", stream=False))
             
response = api.query(query="from my.app.web.activityAll select * limit 10",
                     dates= {'from': "2018-02-06 12:42:00"})
                     
print(response)

api.config.response = "json/compact"

response = api.query(query="from my.app.web.activityAll select * limit 10",
                     dates= {'from': "2018-02-06 12:42:00", 'timeZone': "GMT+2"})
                     
print(response)

```

Real time/stream query:

```python
from devo.api import Client, ClientConfig

api = Client(auth={"key":"myapikey", "secret": "myapisecret"},
             address="https://apiv2-eu.devo.com/search/query", 
             config=ClientConfig(response="json/simple/compact", 
                                 pragmas={"name": "jose_ramon_id123",
                                          "app_name": "sdk-tests-master"}))
             
response = api.query(query="from my.app.web.activityAll select * limit 10",
                     dates= {'from': "2018-02-06 12:42:00"})

try:
    for item in response:
        print(item)
except Exception as error:
    print(error)

```

Query by id has the same parameters as query (), changing the field "query"
to "query_id", which is the ID of the query in Devo.

## Not verify certificates

If server has https certificates with problems, autogenerated or not verified, you can deactivate
 the secure calls (Verifying the certificates https when making the call) disabling it with:

```python
from devo.api import Client, ClientConfig


api = Client(auth= {"key":"myapikey", "secret":"myapisecret"}, 
             address="https://apiv2-eu.devo.com/search/query")
api.verify_certificates(False)
```

You can revert it with:

```python
api.verify_certificates(True)
```  

## Use custom CA to verify

For customs servers, and custom certificates, you can use custom CA for verity that certificates.
You can put CA cert path instead of "False" or "True"

```python
from devo.api import Client, ClientConfig


api = Client(auth= {"key":"myapikey", "secret":"myapisecret"}, 
             address="https://apiv2-eu.devo.com/search/query")
api.verify_certificates("/path/to/cafile.ca")
```

You can revert it with:

```python
api.verify_certificates(True)
```  

## Processors flags

By default, you receive response in str/bytes (Depends of your python version) direct from Socket, and you need manipulate the data.
But you can specify one default processor for data, soo you receive in diferents format:

```python
from devo.api import Client, ClientConfig, JSON_SIMPLE

config = ClientConfig(response="json/simple", processor=JSON_SIMPLE, stream=True)

api = Client(auth={"key":"myapikey", "secret":"myapisecret"},
             address="https://apiv2-eu.devo.com/search/query",
             config=config)
             
response = api.query(query="from my.app.web.activityAll select * limit 10",
                     dates= {'from': "2018-02-06 12:42:00", 'timeZone': "GMT-2"})

try:
    for item in response:
        print(item)
except Exception as error:
    print(error)
```

### Flag list

- DEFAULT: It is the default processor, it returns str or bytes, depending on the Python version
- TO_STR: Return str, decoding data if receive bytes
- TO_BYTES: Return bytes, encoding data if receive str
- JSON: Use it if you want json objects, when ask for json responses, instead of str/bytes. Ignored when response=csv
- JSON_SIMPLE: Use it if you want json objects, when ask for json/simple response, instead of str/bytes.  Ignored when response=csv
- COMPACT_TO_ARRAY: Use it if you want arrays, when ask for json/compact responses, instead of str/bytes. Ignored when response=csv
- SIMPLECOMPACT_TO_OBJ: Use it if you want json objects, when ask for json/simple/compact responses, instead of str/bytes. Ignored when response=csv
- SIMPLECOMPACT_TO_ARRAY: Use it if you want json objects, when ask for json/simple/compact responses, instead of str/bytes. Ignored when response=csv

**JSON_SIMPLE, COMPACT_TO_ARRAY, SIMPLECOMPACT_TO_OBJ and SIMPLECOMPACT_TO_ARRAY only work with the api in mode `stream=True`**

You can change the processor in any moment with one default processor or custom with the function:

```python
from devo.api import Client, ClientConfig, JSON_SIMPLE

config = ClientConfig(response="json/simple", processor=JSON_SIMPLE, stream=True)

api = Client(auth={"key":"myapikey", "secret":"myapisecret"},
             address="https://apiv2-eu.devo.com/search/query",
             config=config)
api.config.set_processor(processor)
```

#### DEFAULT example in Python 3, response csv

```python
b'18/Jan/2019:09:58:51 +0000,/category.screen?category_id=BEDROOM&JSESSIONID=SD10SL6FF10ADFF7,404,http://www.bing.com/,Googlebot/2.1 ( http://www.googlebot.com/bot.html),gaqfse5dpcm690jdh5ho1f00o2:-'
```  

#### DEFAULT example in Python 2.7, response csv

```python
'18/Jan/2019:09:58:51 +0000,/category.screen?category_id=BEDROOM&JSESSIONID=SD10SL6FF10ADFF7,404,http://www.bing.com/,Googlebot/2.1 ( http://www.googlebot.com/bot.html),gaqfse5dpcm690jdh5ho1f00o2:-'
```  

#### TO_STR example in Python 3, response csv

```python
'18/Jan/2019:09:58:51 +0000,/category.screen?category_id=BEDROOM&JSESSIONID=SD10SL6FF10ADFF7,404,http://www.bing.com/,Googlebot/2.1 ( http://www.googlebot.com/bot.html),gaqfse5dpcm690jdh5ho1f00o2:-'
```  

#### TO_BYTES example in Python 2.7, response csv

```python
b'18/Jan/2019:09:58:51 +0000,/category.screen?category_id=BEDROOM&JSESSIONID=SD10SL6FF10ADFF7,404,http://www.bing.com/,Googlebot/2.1 ( http://www.googlebot.com/bot.html),gaqfse5dpcm690jdh5ho1f00o2:-'
```  

#### SIMPLECOMPACT_TO_ARRAY example in Python 3, response json/simple/compact

```python
['18/Jan/2019:09:58:51 +0000', '/category.screen?category_id=BEDROOM&JSESSIONID=SD10SL6FF10ADFF7', 404, 'http://www.bing.com/', 'Googlebot/2.1 ( http://www.googlebot.com/bot.html)', 'gaqfse5dpcm690jdh5ho1f00o2:-']
```  

#### SIMPLECOMPACT_TO_OBJ example in Python 3, response json/simple/compact

```python
{'statusCode': 404, 'uri': '/category.screen?category_id=BEDROOM&JSESSIONID=SD10SL6FF10ADFF7', 'referralUri': 'http://www.bing.com/', 'userAgent': 'Googlebot/2.1 ( http://www.googlebot.com/bot.html)', 'cookie': 'gaqfse5dpcm690jdh5ho1f00o2:-', 'timestamp': '18/Jan/2019:09:58:51 +0000'}
```  

## The "from" and "to", formats and other stuff

Here we define the start and end of the query (query eventdate filter are
secondary), those are the limits of the query.

```
From                                                                          To
|-----------------|OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO|------------------------|
                today()  <=    eventdate      <=    now()
```

### Date Formats

- **Fixed format:** As described on [Official Python Docs](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior). Accepted formats are:
  - '%Y-%m-%d %H:%M:%S'
  - '%Y-%m-%d', the time will be truncated to 00:00:00

- **Timestamp:** From epoch in seconds

- **Dynamic expression:** Using the LinQ sintax we can use several functions. **timeZone can be wrong with this syntax**
  - Relative functions:
    - now(): Current date and time
    - today(): Current date and time fixed to 00:00:00
    - yesterday(): Current date minus one day and time fixed to 00:00:00
  - Amount functions:
    - second(): Return 1
    - minute(): Return 60
    - hour(): Return 60 * 60
    - day(): Return 24 *60* 60
    - week(): Return 7 *24* 60 * 60
    - month(): Return 30 *24* 60 * 60

    With this sintax you can use expressions like: `from="now()-2*day()` equivalent to now minus two days.
    Or `from=today()-6*month()`, etc.

- **New REST API dinamyc dates**:

    `For all the examples that don't use a timestamp to specify a date, we assume that the moment of execution is 08-10-2018, 14:33:12 UTC.`
    This is a copy of official Devo docs you can see [HERE](https://docs.devo.com/confluence/ndt/api-reference/rest-api/running-queries-with-the-rest-api)

### ____***Dates***

|Operator|Example|Description|
| ------------- | ------------- |---------|
|today| |Get the current day at 00:00:00. Note that the timeZone parameter affects the date settings.|
| |`"from": "today"`|This sets the starting date to 08-10-2018, 00:00:00 UTC |
| |`"to": "today"`|This sets the ending date to 08-10-2018, 00:00:00 UTC |
| |`"from": "today", "timeZone": "GMT+2"`|This sets the starting date to 08-10-2018, 00:00:00 GMT+2 (07-10-2018, 22:00:00 UTC) |
| |`"to": "today", "timeZone": "GMT+2"`|This sets the ending date to 08-10-2018, 00:00:00 GMT+2 (07-10-2018, 22:00:00 UTC) |
| | | |
|now| |Get the current day and time |
| |`"from": "now"`|This sets the starting date to 08-10-2018, 14:33:12 UTC |
| |`"to": "now"`|This sets the ending date to 08-10-2018, 14:33:12 UTC |
| | | |
|endday | |If you use this in the from field you will get the current day and the last second of the day. If you use it in the to field you will get the from date and the last second of that day. Note that the timeZone parameter affects the date settings. |
| |`"from": "endday"`|This sets the starting date to 08-10-2018, 23:59:59 UTC |
| |`"from": 1515500531, "to": "endday"`|(this timestamp corresponds to 01/09/2018 12:22:11 UTC) This sets the ending date to 01-09-2018, 23:59:59 UTC. |
| |`"from": "endday", "timeZone": "GMT+2"`|This sets the ending date to 08-10-2018, 23:59:59 GMT+2 (08-10-2018, 21:59:59 UTC) |
| |`"from": 1515493331,  "to": "endday", "timeZone": "GMT+2"`|(this timestamp corresponds to 01/09/2018, 12:22:11 GMT+2) This sets the ending date to 01-09-2018 23:59:59 GMT+2 (01-09-2018, 21:59:59 UTC) |
| |`"from": 1515452400, "to": "endday", "timeZone": "GMT+2"`|(this timestamp corresponds to 01/09/2018, 01:00:00 GMT+2) This sets the ending date to 01-09-2018 23:59:59 GMT+2 (01-09-2018, 21:59:59 UTC) |
| | | |
|endmonth| |If you use this in the from field you will get the last day of the current month and the last second of that day. If you use it in the to field, you will get last day of the month indicated in the date field and the last second of that day. Note that the timeZone parameter affects the date settings. |
| |`"from": "endmonth"`|This sets the starting date to 31-10-2018, 23:59:59 UTC |
| |`"to": "endmonth"`|This sets the ending date to 30-09-2018, 23:59:59 UTC. |
| |`"from": 1536150131, "to": "endmonth"`|(this timestamp corresponds to 05/09/2018, 12:22:11 UTC) This sets the ending date to 30-09-2018, 23:59:59 UTC |
| |`"from": 1536142931, "to": "endmonth", "timeZone": "GMT+2"`|(this timestamp corresponds to 05/09/2018, 12:22:11 GMT+2) This sets the ending date to 30-09-2018 23:59:59 GMT+2 (30-09-2018, 21:59:59 UTC) |

### ____***Days***

|Operator|Example|Description|
| ------------- | ------------- |------------- |
|d | |Enter a number followed by d in the from parameter to substract N days from the current date. If you use it in the to field you will get the from date plus the indicated number of days. |
| |`"from": "2d"`|This sets the starting date to 06-10-2018, 14:33:12 UTC |
| |`"from": 1536150131, "to": "2d"`|This sets the ending date to 07-09-2018, 12:22:11 UTC |
| |`"from": "5d",  "to": "2d"`|This sets the starting date to 03-10-2018, 14:33:12 UTC and the ending date to 05-10-2018, 14:33:12 UTC |
| | | |
|ad| |Enter a number followed by ad in the from parameter to subtract N days from the current date and set time to 00:00:00. If you use it in the to field you will get the from date plus the indicated number of days and set time to 00:00:00. Note that the timeZone parameter affects the date settings. |
| |`"from": "2ad"`|This sets the starting date to 06-10-2018, 00:00:00 UTC |
| |`"from": 1536150131, "to": "2ad"`|(this timestamp corresponds to 05-09-2018, 12:22:11 UTC) This sets the ending date to 07-09-2018, 00:00:00 UTC |
| |`"from":"5ad", "to": "2ad"`|This sets the starting date to 03-10-2018, 00:00:00 UTC and the ending date to 05-10-2018, 00:00:00 UTC |
| |`"from": "5ad", "to": "2ad"`|This sets the starting date to 03-10-2018, 00:00:00 UTC and the ending date to 05-10-2018, 00:00:00 UTC |
| |`"from": 1536142931, "to": "2ad", "timeZone": "GMT+2"`|(this timestamp corresponds to 05-09-2018, 12:22:11 UTC) This sets the ending date to 07-09-2018, 00:00:00 GMT+2 (06-09-2018, 22:00:00 UTC) |
| |`"from": "5ad", "to": "2ad", "timeZone": "GMT+2"`|This sets the starting date to 03-10-2018, 00:00:00 GMT+2 (02-10-2018, 22:00:00 UTC), and the ending date to 05-10-2018, 00:00:00 GMT+2 (04-10-2018, 22:00:00 UTC) |

### ____***Hours***

|Operator|Example|Description|
| ------------- | ------------- |------------- |
|h| |Enter a number followed by h in the from parameter to subtract N hours from the current time. If you use it in the to field you will get the from time plus the indicated number of hours |
| |`"from": "2h"`|This sets the starting date to 08-10-2018, 12:33:12 UTC |
| |`"from": "16h"`|This sets the starting date to 07-10-2018, 22:33:12 UTC |
| |`"from": 1536150131, "to": "2h"`|(this timestamp corresponds to 05/09/2018, 12:22:11 UTC) This sets the ending date to 05-09-2018, 14:22:11 UTC |
| |`"from": "5h", "to": "2h"`|This sets the starting date to 08-10-2018, 09:33:12 UTC and the ending date to 08-10-2018, 11:33:12 UTC |
|ah| |Enter a number followed by ah in the from parameter to subtract N hours from the current date at 00:00:00. If you use it in the to field you will add the indicated number of hours to the from date at 00:00:00. Note that the timeZone parameter affects the date settings. |
| |`"from": "2ah"`|This sets the starting date to 07-10-2018, 22:00:00 UTC |
| |`"from": "2ah", "timeZone": "GMT+2"`|This sets the starting date to 07-10-2018, 22:00:00 GMT+2 (07-10-2018, 20:00:00 UTC) |
| |`"from": 1536114131, "to": "12ah"`|(this timestamp corresponds to 05-09-2018, 02:22:11 UTC) This sets the starting date to 07-10-2018, 22:00:00 GMT+2 (07-10-2018, 20:00:00 UTC) |
| |`"from": 1536106931, "to": "12aH", "timeZone": "GMT+2"`|(this timestamp corresponds to 05-09-2018, 12:22:11 GMT+2) This sets the ending date to 05-09-2018, 12:00:00 GMT+2 (05-09-2018, 10:00:00 UTC) |
| |`"from": "5ah", "to": "21ah"`|This sets the starting date to 07-10-2018, 19:00:00 UTC and the ending date to 07-10-2018, 21:00:00 UTC |

### Retries

The Client supports a retry mechanism for **connectivity issues only**. The retry mechanism is disabled by default (the `retries` parameter is set to `0`by default in the `Client` constructor).

In order to enable it, you must set up the `retries` parameter with a value bigger or equals than `1`. The regular action/command is not considered a retry, only the additional attempts.

There is a delay within `retries`. The default base delay is `5` seconds, it is updated by Exponential backoff algorithm in every retry with a rate reduction of `2`. The base delay is multiplied by 2 in every retry. The base delay can be configured by parameter `retry_delay`

### Keep Alive mechanism support

Some queries may require a big time to start returning data, because of the calculations required, the load of the platform or just because the data belongs to the future (because the data hasn't been ingested yet).

In such a cases, as the client is a common HTTP client, there is a timeout for the server for start returning data. When this deadline is over the client cancels the request, and it returns a timeout error.

In order to avoid this timeout errors, the server returns tokens every little time to reset the timeout control in the client. Client supports the processing of these tokens to not spoil the data and returning the right data.

Client detects and removes tokens from response transparently, so developer has not to deal with them.

Client support several modes for supporting this mechanism. The mode is set up in parameter `keepAliveToken` in `ClientConfig`. Its default value is `devo.api.client.DEFAULT_KEEPALIVE_TOKEN`

* `devo.api.client.NO_KEEPALIVE_TOKEN`: No keep alive token mechanism will be used
  * `json`, `json/compact`, `json/simple` and `json/simple/compact` modes are forced to use always `DEFAULT_KEEPALIVE_TOKEN` mode, so it cannot be disabled for them. The token for these modes is always `b'    '` (four utf-8 spaces chars)
  * For `csv`, `tsv` and `xls` the keep alive mechanism is disabled and no token is sent by server
  * `msgpack` does not support the keep alive mechanism in any case and this is the only valid choice for this response mode
* `devo.api.client.DEFAULT_KEEPALIVE_TOKEN`: The default token used
  * `json`, `json/compact`, `json/simple` and `json/simple/compact` token is always `b'    '` (four utf-8 spaces chars)
  * For `csv`, `tsv` and `xls` token is always `\n` (new line char) in this mode
  * `msgpack` does not support the keep alive mechanism, `NO_KEEPALIVE_TOKEN` is forced
* `devo.api.client.EMPTY_EVENT_KEEPALIVE_TOKEN`: A new empty event or line is created by the server. The format of the event will depend on response mode, `csv`or `tsv`
  * `json`, `json/compact`, `json/simple` and `json/simple/compact` token is always `b'    '` (four utf-8 spaces chars)
  * For `csv` and `tsv` token contains as many separator chars (`,` or `\t`) as columns/fields the response has minus 1, followed by `\n` (new line char)
  * `msgpack` and `xls` do not support this mode
* CUSTOM keep alive token: Any `str` may be a valid token. This `str` will be used by the sever as keep alive token
  * `json`, `json/compact`, `json/simple` and `json/simple/compact` token is always `b'    '` (four utf-8 spaces chars)
  * For `csv` and `tsv` token is the custom `str` set as parameter
  * `msgpack` and `xls` do not support this mode

| Response mode       | default mode              | `NO_KEEPALIVE_TOKEN` | `DEFAULT_KEEPALIVE_TOKEN` | `EMPTY_EVENT_KEEPALIVE_TOKEN` | Custom keep alive token      |
|---------------------|---------------------------|----------------------|---------------------------|-------------------------------|------------------------------|
| json                | `DEFAULT_KEEPALIVE_TOKEN` | `b'    '`            | `b'    '`                 | `b'    '`                     | `b'    '`                    |
| json/compact        | `DEFAULT_KEEPALIVE_TOKEN` | `b'    '`            | `b'    '`                 | `b'    '`                     | `b'    '`                    |
| json/simple         | `DEFAULT_KEEPALIVE_TOKEN` | `b'    '`            | `b'    '`                 | `b'    '`                     | `b'    '`                    |
| json/simple/compact | `DEFAULT_KEEPALIVE_TOKEN` | `b'    '`            | `b'    '`                 | `b'    '`                     | `b'    '`                    |
| msgpack             | `NO_KEEPALIVE_TOKEN`      | *Not supported*      | *Not supported*           | *Not supported*               | *Not supported*              |
| csv                 | `DEFAULT_KEEPALIVE_TOKEN` | Mechanism not used   | `\n`                      | `,+\n` <sup>1</sup>           | `str` *token*                |
| tsv                 | `DEFAULT_KEEPALIVE_TOKEN` | Mechanism not used   | `\n`                      | `\t+\n` <sup>1</sup>          | `str`*token*                 |
| xls                 | `NO_KEEPALIVE_TOKEN`      | *Not supported*      | *Not supported*           | *Not supported* <sup>2</sup>  | *Not supported* <sup>2</sup> |

<sup>1</sup> the `csv` and `tsv` token contains as many separator chars (`,` or `\t`) as columns/fields the response has minus 1, followed by `\n` (new line char)

<sup>2</sup> `xls` does support `EMPTY_EVENT_KEEPALIVE_TOKEN` by inserting empty lines in Excel file. As the Client can not *clean* these lines, the mode was not supported in this implementation.

## CLI USAGE

Usage: `devo-api query [OPTIONS]`

  Perform query by query string

```
Options:
  -c, --config PATH       Optional JSON/Yaml File with configuration info.
  -e, --env TEXT          Use env vars for configuration
  -d, --default TEXT      Use default file for configuration
  -a, --address TEXT      Endpoint for the api.
  --user TEXT             User for the api.
  --app_name TEXT         Application name for the api.
  --comment TEXT          Comment for the queries.
  --key TEXT              Key for the api.
  --secret TEXT           Secret for the api.
  --token TEXT            Secret for the api.
  --jwt TEXT              JWT auth for the api.
  -q, --query TEXT        Query.
  --stream / --no-stream  Flag for make streaming query or full query with
                          start and end. Default is true

  --output TEXT           File path to store query response if not want stdout
  -r, --response TEXT     The output format. Default is json/simple/compact
  --from TEXT             From date. For valid formats see API README. Default
                          if now - 1 hour

  --to TEXT               To date. For valid formats see API README
  --timeZone TEXT         Timezone info. For valid formats see API README
  --verify BOOLEAN        Verify certificates
  --debug / --no-debug    For testing purposes
  --help                  Show this message and exit.
```

A configuration file does not have to have all the necessary keys, you can have
the common values: url, port, certificates. And then send with the call the tag,
 file to upload, etc.

Both things are combined at runtime, prevailing the values that are sent as
arguments of the call over the configuration file

**Config file key:** The CLI uses the API key to query the data.
You can see one examples in tests folders

json example 1:

```json
  {
    "api": {
      "key": "MyAPIkeytoaccessdevo",
      "secret": "MyAPIsecrettoaccessdevo",
      "address": "https://apiv2-us.devo.com/search/query"
    }
  }
  
```

json example 2:

```json
  {
    "api": {
      "auth": {
        "key": "MyAPIkeytoaccessdevo",
        "secret": "MyAPIsecrettoaccessdevo",
      },
      "address": "https://apiv2-us.devo.com/search/query"
    }
  }
  
```

yaml example 1:

```yaml
  api:
    key: "MyAPIkeytoaccessdevo"
    secret: "MyAPIsecrettoaccessdevo"
    address: "https://apiv2-us.devo.com/search/query"
```

yaml example 2:

```yaml
  api:
    auth:
      key: "MyAPIkeytoaccessdevo"
      secret: "MyAPIsecrettoaccessdevo"
    address: "https://apiv2-us.devo.com/search/query"
```

You can use environment variables or a global configuration file for the KEY, SECRET, URL, USER, APP_NAME and COMMENT values

How do the CLI resolve the set up of this parameters? This is the evalutaion order:

1. `-c` configuration file option: use it to set API key, secret and url, or token and url in one file.
2. The parameters in CLI call can complete values not in configuration file, but not override it
3. Environment vars: if you set key, secrey or token in config file or params cli, this option should not be used.
4. ~/.devo.json or ~/.devo.yaml: if you set key, secrey or token in other way, this option should not be used.

Environment vars are:

- `DEVO_API_ADDRESS`
- `DEVO_API_KEY`
- `DEVO_API_SECRET`
- `DEVO_API_USER`
- `DEVO_API_TOKEN`
- `DEVO_API_JWT`

## Choosing Format

The default response format (`response`) is `json`, to change the default value, it can be established directly:

```python
api.response = 'json/compact'
```

To change the response format (`format`) of a query, just change the value of the attribute response of the query call

```python
api.config.response = config.get('response')

response = api.query(config.get('query'), 
                     dates={"from": config.get('from'), "to": config.get('to')})
```

Format allow the following values:

- json
- json/compact
- json/simple
- json/simple/compact
- msgpack
- csv (comma separated values)
- tsv (Tab separated Values)

### Response type JSON

When `response` is set to `json`, response is a
Json Object with the following structure:

| Field Name | Type | Description |
|---|---|---|
| success | boolean | True → ok<br />False → error  |
| msg | String | Message Description in case of error |
| status | Integer | Numeric value  that especify the error code. <br /> 0 - OK<br /> 1 - Invalid request |
| object | Json Object | The Query Result. The format of the content, depends on the Query data. |

Example

```python
{
 "success": True,
 "status": 0,
 "msg": "valid request",
 "object": [
   {
     "eventdate": "2016-10-24 06:35:00.000",
     "host": "aws-apiodata-euw1-52-49-216-97",
     "memory_heap_used": "3.049341704E9",
     "memory_non_heap_used": "1.21090632E8"
   },
   {
     "eventdate": "2016-10-24 06:36:00.000",
     "host": "aws-apiodata-euw1-52-49-216-97",
     "memory_heap_used": "3.04991028E9",
     "memory_non_heap_used": "1.21090632E8"
   },
   {
     "eventdate": "2016-10-24 06:37:00.000",
     "host": "aws-apiodata-euw1-52-49-216-97",
     "memory_heap_used": "3.050472496E9",
     "memory_non_heap_used": "1.21090632E8"
   }
 ]
}
```

### Response type json/compact

When `response` is set to `json/compact`, response is a
Json Object with the following structure:

| Field Name | Type | Description |
|---|---|---|
| success | boolean | True → ok<br />False → error  |
| msg | String | Message Description in case of error |
| status | Integer | Numeric value  that especify the error code. <br /> 0 - OK<br /> 1 - Invalid request |
| object | Json Object |  |
| object.m | Json Object | Json Object with Metadata information, the key is the name of the field, and the value is an Object with the following information:. <ul><li><b>type:</b> type of the value returned:  <ul><li>timestamp: epoch value in seconds   </li><li>str: string   </li><li>int8: 8 byte integer </li><li>int4: 4 byt integer   </li><li>bool: boolean   </li><li>float8: 8 byte floating point.    </li></ul></li><li><b>index:</b> integer value, that points to where in the array of values is the value of this field </li></ul> |
| object.d | Json Object | Array of Arrays with the values of the response of the query. |

Example

```python
{
    "msg": "",
    "status": 0,
    "object": {
        "m": {
            "eventdate": {
                "type": "timestamp",
                "index": 0
            },
            "domain": {
                "type": "str",
                "index": 1
            },
            "userEmail": {
                "type": "str",
                "index": 2
            },
            "country": {
                "type": "str",
                "index": 3
            },
            "count": {
                "type": "int8",
                "index": 4
            }
        },
"d": [
        [
            1506442210000,
            "self",
            "luis.xxxxx@devo.com",
            null,
            2
        ],
        [
            1506442220000,
            "self",
            "goaquinxxx@gmail.com",
            null,
            2
        ],
    .....
    ]
}
```

### Response type json/simple

When `response` is set to `json/simple`  
The response is a stream of Json Objects with the following structure of the values that the Query generates, separated each registry  CRLF.

When the query does not generate more information, the connection is closed by the server.

In case, no date to is requested, the connections is keeped alive.

Example

```python
{"eventdate":1488369600000,"domain":"none","userEmail":"","country":null,"count":3}
{"eventdate":1488369600000,"domain":"email@devo.com","userEmail":"0:0:0:0:0:0:0:1","country":null,"count":18}
{"eventdate":1488369600000,"domain":"none","userEmail":"email@devo.com","country":null,"count":7}
{"eventdate":1488373200000,"domain":"email@devo.com","userEmail":"127.0.0.1","country":null,"count":10}
{"eventdate":1488373200000,"domain":"email@devo.com","userEmail":"0:0:0:0:0:0:0:1","country":null,"count":28}
{"eventdate":1488373200000,"domain":"self","userEmail":"email@devo.com","country":null,"count":15}
{"eventdate":1488373200000,"domain":"self","userEmail":"email@devo.com","country":null,"count":49}
{"eventdate":1488376800000,"domain":"email@devo.com","userEmail":"127.0.0.1","country":null,"count":10}
{"eventdate":1488376800000,"domain":"self","userEmail":"email@devo.com","country":null,"count":16}
{"eventdate":1488376800000,"domain":"email@devo.com","userEmail":"0:0:0:0:0:0:0:1","country":null,"count":5}
{"eventdate":1488376800000,"domain":"self","userEmail":"email@devo.com","country":null,"count":35}
{"eventdate":1488376800000,"domain":"self","userEmail":"email@devo.com","country":null,"count":128}
{"eventdate":1488376800000,"domain":"self","userEmail":"email@gmail.com","country":null,"count":7}
{"eventdate":1488376800000,"domain":"self","userEmail":"email@devo.com","country":null,"count":3}
{"eventdate":1488380400000,"domain":"email@devo.com","userEmail":"127.0.0.1","country":null,"count":21}
{"eventdate":1488380400000,"domain":"self","userEmail":"email@devo.com","country":null,"count":71}
{"eventdate":1488380400000,"domain":"email@devo.com","userEmail":"0:0:0:0:0:0:0:1","country":null,"count":38}
{"eventdate":1488380400000,"domain":"self","userEmail":"email@devo.com","country":null,"count":1}
...
```

### Response type json/simple/compact

When `response` is set to `json/simple/compact`  
The response is a stream of Json Objects with the following structure each line is  separated by  CRLF:

The First Line is a JSON object  map with the Metadata information, the key is the name of the field, and the value is a Object with the following information:

```python
{"m":{"eventdate":{"type":"timestamp","index":0},"domain":{"type":"str","index":1},"userEmail":{"type":"str","index":2},"country":{"type":"str","index":3},"count":{"type":"int8","index":4}}}
```

<ul><li><b>type:</b> type of the value returned:  <ul><li>timestamp: epoch value in seconds   </li><li>str: string   </li><li>int8: 8 byte integer </li><li>int4: 4 byt integer   </li><li>bool: boolean   </li><li>float8: 8 byte floating point.    </li></ul></li><li><b>index:</b> integer value, that points to where in the array of values is the value of this field </li></ul>

The rest of the lines are data lines:  

```python
{"d":[1506439800000,"self","email@devo.com",null,1]}
```

a field with name "d", gives access to the array of values with the information.

When the query does not generate more information, the connection is closed by the server.  
In case, no date to is requested, the connections is keeped alive.

Example

```python
{"m":{"eventdate":{"type":"timestamp","index":0},"domain":{"type":"str","index":1},"userEmail":{"type":"str","index":2},"country":{"type":"str","index":3},"count":{"type":"int8","index":4}}}
{"d":[1506439800000,"self","email@devo.com",null,1]}
{"d":[1506439890000,"self","email@devo.com",null,1]}
{"d":[1506439940000,"self","email@devo.com",null,1]}
{"d":[1506439950000,"self","email@devo.com",null,1]}
{"d":[1506440130000,"self","email@devo.com",null,1]}
{"d":[1506440130000,"self","email@devo.com",null,2]}
{"d":[1506440170000,"self","email@devo.com",null,3]}
{"d":[1506440200000,"self","email@devo.com",null,3]}
{"d":[1506440220000,"self","email@devo.com",null,1]}
{"d":[1506440230000,"self","email@devo.com",null,1]}
{"d":[1506440260000,"self","email@devo.com",null,3]}
{"d":[1506440270000,"self","email@devo.com",null,1]}
{"d":[1506440280000,"self","email@devo.com",null,1]}
{"d":[1506440280000,"self","email@devo.com",null,1]}
{"d":[1506440290000,"self","email@devo.com",null,3]}
{"d":[1506440350000,"self","email@devo.com",null,1]}
```

### Response type msgpack

When `response` is set to `msgpack`  
The response format is the same that the Json format, but encoded using MsgPack an efficient binary serialization format (<http://msgpack.org/>)

### Response type csv

When `response` is set to `csv`  
The system returns the information in CSV(Comma Separated Values) format, as follows

Example:

```text
    eventdate,domain,userEmail,country,count
    2017-03-01 12:00:00.000,none,,,3
    2017-03-01 12:00:00.000,email@devo.com,0:0:0:0:0:0:0:1,,18
    2017-03-01 12:00:00.000,none,email@devo.com,,7
    2017-03-01 13:00:00.000,email@devo.com,127.0.0.1,,10
    2017-03-01 13:00:00.000,email@devo.com,0:0:0:0:0:0:0:1,,28
    2017-03-01 13:00:00.000,self,email@devo.com,,15
    2017-03-01 13:00:00.000,nombre,email@devo.com,,49
    2017-03-01 14:00:00.000,email@devo.com,127.0.0.1,,10
    2017-03-01 14:00:00.000,self,email@devo.com,,16
    2017-03-01 14:00:00.000,email@devo.com,0:0:0:0:0:0:0:1,,5
    2017-03-01 14:00:00.000,self,email@devo.com,,35
    2017-03-01 14:00:00.000,nombre,email@devo.com,,128
    2017-03-01 14:00:00.000,self,email@gmail.com,,7
    2017-03-01 14:00:00.000,self,email@devo.com,,3
    2017-03-01 15:00:00.000,email@devo.com,127.0.0.1,,21
    2017-03-01 15:00:00.000,self,email@devo.com,,71
    2017-03-01 15:00:00.000,email@devo.com,0:0:0:0:0:0:0:1,,38
    2017-03-01 15:00:00.000,self,email@devo.com,,1
    2017-03-01 15:00:00.000,nombre,email@devo.com,,80
```

### Response type tsv

When `response` is set to `tsv`  
The system returns the information in TSV (Tab Separated Values)  format as follows

Example

```text
    eventdate   domain  userEmail   country count
    2017-03-01 12:00:00.000 none            3
    2017-03-01 12:00:00.000 email@devo.com    0:0:0:0:0:0:0:1     18
    2017-03-01 12:00:00.000 none    email@devo.com        7
    2017-03-01 13:00:00.000 email@devo.com    127.0.0.1       10
    2017-03-01 13:00:00.000 email@devo.com    0:0:0:0:0:0:0:1     28
    2017-03-01 13:00:00.000 self    email@devo.com     15
    2017-03-01 13:00:00.000 nombre email@devo.com       49
    2017-03-01 14:00:00.000 email@devo.com    127.0.0.1       10
    2017-03-01 14:00:00.000 self    email@devo.com        16
    2017-03-01 14:00:00.000 email@devo.com    0:0:0:0:0:0:0:1     5
    2017-03-01 14:00:00.000 self    email@devo.com     35
    2017-03-01 14:00:00.000 nombre email@devo.com       128
    2017-03-01 14:00:00.000 self    email@gmail.com       7
    2017-03-01 14:00:00.000 self    email@devo.com     3
    2017-03-01 15:00:00.000 email@devo.com    127.0.0.1       21
    2017-03-01 15:00:00.000 self    email@devo.com        71
    2017-03-01 15:00:00.000 email@devo.com    0:0:0:0:0:0:0:1     38
```

## Exceptions and Errors

Every issue or error found during the request of queries of data is reported through
`DevoClientException` exception. But since version `5.1.0` there are additional exception classes
for a more detailed feedback of errors:

* `devo.api.client.DevoClientException`: Common legacy Exception class that is thrown for every
error during the querying of data. It inherits from `Exception` class
* `devo.api.client.DevoClientRequestException`: Specific exception class that is thrown whenever
a query is requested to the server endpoint and it fails due to internal errors or bad requests. It
contains the whole `requests.models.Response` from server for reference. It inherits from
`DevoClientException`
* `devo.api.client.DevoClientDataResponseException`: Specific exception class that is thrown
whenever a query (of type stream) is run correctly but an error is thrown when processing one
specific event of the response. It is only thrown for streamed queries. It inherits from
`DevoClientException`
