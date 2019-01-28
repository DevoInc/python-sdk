# Devo API (Client)
## Overview
This library performs queries to the Client API (Search rest api) of Devo.


## USAGE
#### Constructor

- key: The key of the domain
- secret: The secret of the domain
- token: Auth token
- jwt: JWT token
- url(optional): The url of the service. A static constants are provided with
the commons clouds: can take several values, for example:
    - Client.URL_AWS_EU: https://api-eu.logtrust.com
    - Client.URL_AWS_USA: https://api-us.logtrust.com
    - Client.URL_VDC: https://spainapi.logtrust.com
    - Client.URL_QUERY_COMPLEMENT = '/search/query'
- buffer (optional): Buffer object if you modify the Devo Buffer class

    
```python
from devo.api import Client

api = Client(key="myapikey",
             secret="myapisecret",
             url="https://api-eu.logtrust.com/search/query",
             user="user@devo.com",
             app_name="testing app")


api = Client(token="myauthtoken",
             url="https://api-eu.logtrust.com/search/query")

api = Client(jwt="myauthtoken",
             url="https://api-eu.logtrust.com/search/query")
```    
    
#### query() params

`def query(self, **kwargs)`
- query: Query to perform
- query_id: if not query, you can send the query id
- dates: {'from': string, 'to': string} -> Date from and date to, if not "to", in object, to = now()
- response: Type of response from Client API
- limit: Limits of rows returned
- offset: Row number by which to start returning data
- stream: Not wait for all response for return lines - real time mode if not "to" in dates
- response: response type
- processor: response processor flag from defaults
- comment: Comment for the query
- verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.

#### Result returned:
###### - Non stream call
 - Result of the query in str/bytes when query work
 - JSON Object when query has errors
###### - stream call
 - Generator with result of the query, str/bytes, when query work
 - JSON Object when query has errors

Normal/Non stream response:
```python
from devo.api import Client

api = Client(key="myapikey",
             secret="myapisecret",
             url="https://api-eu.logtrust.com/search/query",
             user="user@devo.com",
             app_name="testing app")
             
response = api.query(query="from my.app.web.activityAll select * limit 10",
                     dates= {'from': "2018-02-06 12:42:00"},
                     response="json",
                     stream=False)
                     
print(response)
```

Real time/stream query:
```python
from devo.api import Client

api = Client(key="myapikey",
             secret="myapisecret",
             url="https://api-eu.logtrust.com/search/query",
             user="user@devo.com",
             app_name="testing app")
             
response = api.query(query="from my.app.web.activityAll select * limit 10",
                     dates= {'from': "2018-02-06 12:42:00"},
                     response="json/simple/compact")

try:
    for item in response:
        print(item)
except Exception as error:
    print(error)

```
Query by id has the same parameters as query (), changing the field "query" 
to "query_id", which is the ID of the query in Devo.

## Processors flags:

By default, you receive response in str/bytes (Depends of your python version) direct from Socket, and you need manipulate the data.
But you can specify one default processor for data, soo you receive in diferente format:


```python
from devo.api import Client, JSON_SIMPLE

api = Client(key="myapikey",
             secret="myapisecret",
             url="https://api-eu.logtrust.com/search/query",
             user="user@devo.com",
             app_name="testing app")
             
response = api.query(query="from my.app.web.activityAll select * limit 10",
                     dates= {'from': "2018-02-06 12:42:00"},
                     response="json/simple", processor=JSON_SIMPLE)

try:
    for item in response:
        print(item)
except Exception as error:
    print(error)

```

####Flag list:

- DEFAULT: It is the default processor, it returns str or bytes, depending on the Python version
- TO_STR: Return str, decoding data if receive bytes
- TO_BYTES: Return bytes, encoding data if receive str
- JSON: Use it if you want json objects, when ask for json responses, instead of str/bytes. Ignored when response=csv
- JSON_SIMPLE: Use it if you want json objects, when ask for json/simple response, instead of str/bytes.  Ignored when response=csv
- COMPACT_TO_ARRAY: Use it if you want arrays, when ask for json/compact responses, instead of str/bytes. Ignored when response=csv
- SIMPLECOMPACT_TO_OBJ: Use it if you want json objects, when ask for json/simple/compact responses, instead of str/bytes. Ignored when response=csv
- SIMPLECOMPACT_TO_ARRAY: Use it if you want json objects, when ask for json/simple/compact responses, instead of str/bytes. Ignored when response=csv


######- DEFAULT example in Python 3, response csv: 
```python
b'18/Jan/2019:09:58:51 +0000,/category.screen?category_id=BEDROOM&JSESSIONID=SD10SL6FF10ADFF7,404,http://www.bing.com/,Googlebot/2.1 ( http://www.googlebot.com/bot.html),gaqfse5dpcm690jdh5ho1f00o2:-'
```  

######- DEFAULT example in Python 2.7, response csv: 
```python
'18/Jan/2019:09:58:51 +0000,/category.screen?category_id=BEDROOM&JSESSIONID=SD10SL6FF10ADFF7,404,http://www.bing.com/,Googlebot/2.1 ( http://www.googlebot.com/bot.html),gaqfse5dpcm690jdh5ho1f00o2:-'
```  
######- TO_STR example in Python 3, response csv: 
```python
'18/Jan/2019:09:58:51 +0000,/category.screen?category_id=BEDROOM&JSESSIONID=SD10SL6FF10ADFF7,404,http://www.bing.com/,Googlebot/2.1 ( http://www.googlebot.com/bot.html),gaqfse5dpcm690jdh5ho1f00o2:-'
```  
######- TO_BYTES example in Python 2.7, response csv: 
```python
b'18/Jan/2019:09:58:51 +0000,/category.screen?category_id=BEDROOM&JSESSIONID=SD10SL6FF10ADFF7,404,http://www.bing.com/,Googlebot/2.1 ( http://www.googlebot.com/bot.html),gaqfse5dpcm690jdh5ho1f00o2:-'
```  
######- SIMPLECOMPACT_TO_ARRAY example in Python 3, response json/simple/compact: 
```python
['18/Jan/2019:09:58:51 +0000', '/category.screen?category_id=BEDROOM&JSESSIONID=SD10SL6FF10ADFF7', 404, 'http://www.bing.com/', 'Googlebot/2.1 ( http://www.googlebot.com/bot.html)', 'gaqfse5dpcm690jdh5ho1f00o2:-']
```  
######- SIMPLECOMPACT_TO_OBJ example in Python 3, response json/simple/compact: 
```python
{'statusCode': 404, 'uri': '/category.screen?category_id=BEDROOM&JSESSIONID=SD10SL6FF10ADFF7', 'referralUri': 'http://www.bing.com/', 'userAgent': 'Googlebot/2.1 ( http://www.googlebot.com/bot.html)', 'cookie': 'gaqfse5dpcm690jdh5ho1f00o2:-', 'timestamp': '18/Jan/2019:09:58:51 +0000'}
```  

## The "from" and "to", formats and other stuff...
Here we define the start and end of the query (query eventdate filter are
secondary), those are the limits of the query.

```
From                                                                          To
|-----------------|OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO|------------------------|
                today()  <=    eventdate      <=    now()
```

### Date Formats
- Fixed format: As described on [Official Python Docs](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior). Accepted formats are:
    - '%Y-%m-%d %H:%M:%S'
    - '%Y-%m-%d', the time will be truncated to 00:00:00
- Timestamp: From epoch in millis
- Dynamic expression: Using the LinQ sintax we can use several functions
    - Relative functions:
        - now(): Current date and time
        - today(): Current date and time fixed to 00:00:00
        - yesterday(): Current date minus one day and time fixed to 00:00:00
    - Amount functions:
        - second(): Return 1
        - minute(): Return 60
        - hour(): Return 60 * 60
        - day(): Return 24 * 60 * 60
        - week(): Return 7 * 24 * 60 * 60
        - month(): Return 30 * 24 * 60 * 60


## CLI USAGE

Usage: `devo-api query [OPTIONS]`

  Perform query by query string

```
Options:
  -c, --config PATH                            JSON/YAML File with configuration, you can put all options here
  -u, --url TEXT                               Endpoint for the api.
  --api_key, --apiKey, --key TEXT              Key for the api.
  --api_secret, --apiSecret, --secret TEXT     Secret for the api.
  --auth_token, --authToken, --token TEXT      Token auth for query.
  --jwt TEXT                                   jwt auth for query.
  -q, --query TEXT                             Query.
  --stream / --no-stream                       Flag for make streaming query or full query with start and end. Default is true
  --output TEXT                                File path to store query response if not want stdout
  -r, --response TEXT                          The output format. Default is json/simple/compact
  --from TEXT                                  From date, and time for the query (YYYY-MM-DD hh:mm:ss). For valid formats see lt-common README
  --to TEXT                                    To date, and time for the query (YYYY-MM-DD hh:mm:ss). For valid formats see lt-common README
  --help                                       Show this message and exit.
  -user                                        User for the api.
  -app_name                                    App Name for the api.
```

A configuration file does not have to have all the necessary keys, you can have 
the common values: url, port, certificates. And then send with the call the tag,
 file to upload, etc.

Both things are combined at runtime, prevailing the values that are sent as 
arguments of the call over the configuration file

**Config file key:** The CLI uses the "api" key to search for information. 
You can see one examples in tests folders

json example:
```json
  {
    "api": {
      "key": "MyAPIkeytoaccessdevo",
      "secret": "MyAPIsecrettoaccessdevo",
      "url": "https://api-us.logtrust.com/search/query"
    }
  }
  
```

yaml example:
```yaml
  api:
    key: "MyAPIkeytoaccessdevo"
    secret: "MyAPIsecrettoaccessdevo"
    url: "https://api-us.logtrust.com/search/query"
```

You can use environment variables or a global configuration file for the KEY, SECRET, URL, USER, APP_NAME and COMMENT values

Priority order:
1. -c configuration file option: if you use ite, CLI search key, secret and url, or token and url in the file
2. params in CLI call: He can complete values not in configuration file, but not override it
3. Environment vars: if you send key, secrey or token in config file or params cli, this option not be called
4. ~/.devo.json or ~/.devo.yaml: if you send key, secrey or token in other way, this option not be called

Environment vars are: `DEVO_API_URL`, `DEVO_API_KEY`, `DEVO_API_SECRET`, `DEVO_API_USER`.

## Choosing Fomat
The default response format (`response`) is `json`, to change the default value, it can be established directly:

```python
api.response = 'json/compact'
```

To change the response format (`format`) of a query, just change the value of the attribute response of the query call
```python
response = api.query(config['query'], 
                     date_from=config['from'], 
                     date_to=config['to'], 
                     response=config['response'])
```

Type allow the following values:

    · json
    · json/compact
    · json/simple
    · json/simple/compact
    · msgpack
    · csv (comma separated values)
    · tsv (Tab separated Values)
    
    
#### Response type JSON 

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

#### Response type json/compact

When `response` is set to `json/compact`, response is a
Json Object with the following structure:

| Field Name | Type | Description |
|---|---|---|
| success | boolean | True → ok<br />False → error  |
| msg | String | Message Description in case of error |
| status | Integer | Numeric value  that especify the error code. <br /> 0 - OK<br /> 1 - Invalid request |
| object | Json Object |  |
| object.m | Json Object | Json Object with Metadata information, the key is the name of the field, and the value is an Object with the following information:. <ul><li><b>type:</b> type of the value returned:  <ul><li>timestamp: epoch value in milliseconds   </li><li>str: string   </li><li>int8: 8 byte integer </li><li>int4: 4 byt integer   </li><li>bool: boolean   </li><li>float8: 8 byte floating point.    </li></ul></li><li><b>index:</b> integer value, that points to where in the array of values is the value of this field </li></ul> | 
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


#### Response type json/simple

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

#### Reponse type json/simple/compact

When `response` is set to `json/simple/compact`  
The response is a stream of Json Objects with the following structure each line is  separated by  CRLF:

The First Line is a JSON object  map with the Metadata information, the key is the name of the field, and the value is a Object with the following information:

```python
{"m":{"eventdate":{"type":"timestamp","index":0},"domain":{"type":"str","index":1},"userEmail":{"type":"str","index":2},"country":{"type":"str","index":3},"count":{"type":"int8","index":4}}}
```

<ul><li><b>type:</b> type of the value returned:  <ul><li>timestamp: epoch value in milliseconds   </li><li>str: string   </li><li>int8: 8 byte integer </li><li>int4: 4 byt integer   </li><li>bool: boolean   </li><li>float8: 8 byte floating point.    </li></ul></li><li><b>index:</b> integer value, that points to where in the array of values is the value of this field </li></ul>

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
    


#### Response type msgpack

When `response` is set to `msgpack`  
The response format is the same that the Json format, but encoded using MsgPack an efficient binary serialization format (http://msgpack.org/)



#### Response type csv

When `response` is set to `csv`  
The system returns the information in CSV(Comma Separated Values) format, as follows

Example

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

#### Response type tsv

When `response` is set to `tsv`  
The system returns the information in TSV (Tab Separated Values)  format as follows

Example

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

