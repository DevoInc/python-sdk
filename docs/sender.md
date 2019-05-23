# Devo Sender
## Overview

This library allows you to send logs or lookups to the Devo platform.

## Features
- Data and lookups sending merged in one procedure
- Allows to send real time data
- Logger integration and logging handler capacity for Sender

## Endpoints
##### Sender
To send data with Devo SDK, first choose the required endpoint depending on the region your are accessing from:
 * **USA:** 	
    * **url**: collector-us.devo.io
    * **port**: 443
 * **EU:**
    * **url**: collector-eu.devo.io
    * **port**: 443
 * **VDC:**
    * **url**: collector-es.devo.io
    * **port**: 443

You have more information in the official documentation of Devo, [Sending data to Devo](https://docs.devo.com/confluence/ndt/sending-data-to-devo).


## Usage in script
### Sender

Before sending the lookup information it is necessary to initialize the collector configuration

#### Initializing the collector

There are different ways (and types) to initialize the collector configuration

Variable descriptions

+ address **(_string_)**: host name to send data
+ port **(_int_)**: port
+ cert_reqs **(_boolean__)**: indicates if certificate is required
+ key **(_string_)**: key file path
+ cert **(_string_)**: cert file path
+ chain **(_string_)**: chain file path
+ tag **(_string_)**: remote table name

- With certificates:
	
```python
from devo.sender import SenderConfigSSL, Sender
engine_config = SenderConfigSSL(address=SERVER, port=PORT,key=KEY, cert=CERT,chain=CHAIN)
con = Sender(engine_config)
```
	
- Without certificates SSL

```python
from devo.sender import SenderConfigSSL, Sender
engine_config = SenderConfigSSL(address=SERVER, port=PORT, cert_reqs=False)
con = Sender(engine_config)
```
	
- Without certificates TCP
	
```python
from devo.sender import SenderConfigTCP, Sender
engine_config = SenderConfigTCP(address=SERVER, port=PORT)
con = Sender(engine_config)
```
	

- From config function - TCP example
```python
from devo.sender import Sender
con = Sender.from_config({"address": "relayurl", "port": 443, "type": "TCP"})
```

- From config function - SSL example
```python
from devo.sender import Sender
con = Sender.from_config({"address": "relayurl", "port": 443, "key": "/tmp/key.key", "cert": "/tmp/cert.cert", "chain": "/tmp/chain.crt"})
```

- From a file

The file must contain a json or YAML format structure with the values into _sender_ variable. The variables will depend of certificate type.

This is a json example:

```json
{   
    "sender": {
	        "address":"devo-relay",
	        "port": 443,
	        "key": "/devo/certs/key.key",
	        "cert": "/devo/certs/cert.crt",
	        "chain": "/devo/certs/chain.crt"
	    },
}
```

This is a yaml example:

```yaml
sender":
  address:"devo-relay"
  port: 443
  key: "/devo/certs/key.key"
  cert: "/devo/certs/cert.crt"
  chain: "/devo/certs/chain.crt"
```

To initialize the collector configuration from a file we need to import **Configuration** class

```python
from devo.common import Configuration

conf = Configuration()
conf.load_config("./config.json.example", 'sender')
config = conf.get()
con = Sender.from_config(config)
```

#### Sending data 

- After we use the configuration class, we will now be able to send events to the collector

```python
from devo.sender import SenderConfigSSL
con = Sender(engine_config)   
```

- send logs to the collector,

```python
con.send(tag="test.drop.actors", msg='Hasselhoff vs Cage')
```
- Send raw log to collector

```python
con.send_raw('<14>Jan  1 00:00:00 Nice-MacBook-Pro.local'
        'test.drop.actors: Testing this random tool')
```

## Optional fields for send function:
+ log_format **(_string_)**: Log format to send
+ facility **(_int_)**: facility user
+ severity **(_int_)**: severity info
+ hostname **(_string_)**: set hostname machine
+ multiline **(_bool_)**: Default False. For multiline msg
+ zip **(_bool_)**: Default False. For send data zipped

## Zip sending:

With the Devo Sender you can make a compressed delivery to optimize data transfer, 
with the restriction that you have to work with bytes (default type for text strings in 
Python 3) and not with str.


```python
con = Sender(engine_config) 
con.send(tag=b"test.drop.actors", msg=b'Hasselhoff vs Cage', zip=True)
con.flush_buffer()
```

The compressed delivery will store the messages in a buffer that, when it is filled, will compress and send, so you have to take into account that you have to execute the _flush_buffer_ function at the end of the data transfer loop, to empty the possible data that have been left uncompressed and send.

**Its important flush the buffer when you're done using it.**

The default buffer length its _19500_ and you can change it with:

```python
con.max_zip_buffer = 19500
```

You can change the default compression level with:

```python
con.compression_level = 6
```

compression_level is an integer from 0 to 9 or -1 controlling the level of compression; 1 (Z_BEST_SPEED) is the fastest and produces the lower compression, 9 (Z_BEST_COMPRESSION) is the slowest and produces the highest compression. 0 (Z_NO_COMPRESSION) has no compression. The default value is -1 (Z_DEFAULT_COMPRESSION). Z_DEFAULT_COMPRESSION represents a default compromise between speed and compression (currently equivalent to level 6).


### Extra info when send: 
`send()`, `send_raw()`, `flush_buffer` and `fill_buffer()` return the numbers of lines sent
 (1, each time, if not zipped, 0..X if zipped)
 
 
## Sender as an Logging Handler
In order to use **Sender** as an Handler, for logging instances, the **tag** property must be set either through the constructor or using the object method: *set_logger_tag(tag)*.

The regular use of the handler can be observed in this  examples:

##### Second example: Setting up a Sender with tag
```python
from devo.common import get_log
from devo.sender import Sender, SenderConfigSSL

engine_config = SenderConfigSSL(address=("devo.collector", 443),
                                key="key.key", cert="cert.crt",
                                chain="chain.crt")
                                
con = Sender.for_logging(engine_config, "my.app.test.logger")
logger = get_log(name="devo_logger", handler=con)
logger.info("Hello devo!")

```
##### Second example: Setting up a static Sender

```python
from devo.common import get_log
from devo.sender import Sender
config = {"address": "devo.collertor", "port": 443,
                 "key": "key.key", "cert": "cert.crt",
                 "chain": "chain.crt", "type": "SSL"}
#Static Sender
con = Sender.for_logging(config=config, tag="my.app.test.logging")
logger = get_log(name="devo_logger", handler=con)
```


###Lookup

Just like the send events case, to create a new lookup or send data to existent lookup table we need to initialize the collector configuration (as previously shown).

In case to initialize the collector configuration from a json/yaml file, you must include a new object into the _lookup_ variable with the next parameters:

+ **name**: lookup table name
+ **file**: CSV file path
+ **lkey**: lookup column key

Example:

```
{   
    "lookup": {
        "name": "Test_Lookup_of_180306_02",
        "file": "test_lookup.csv",
        "lkey": "KEY"
    }
}
```

After initializing the colletor, you must initialize the lookup class.

+ name **(_string_)**: lookup table name
+ historic_tag **(_boolean_)**: save historical
+ con **(_LtSender_)**: Sender conection

```python
    lookup = Lookup(name=config['name'], historic_tag=None, con=con)
```

##### Send lookups from CSV file

After initializing the lookup, you can upload a CSV file with the lookup data by _send_csv_ method from _LtLookup_ class.

Params

+ path **(_string_ required)**: CSV file path
+ has_header **(_boolean_ default: True)**: CSV has header
+ delimiter **(_string_ default: ',')**: CSV delimiter
+ quotechar **(_string_ default: '"')**: CSV quote char
+ headers **(_list_ default: [])**: header array
+ key **(_string_ default: 'KEY')**: lookup key
+ historic_tag **(_string_ default: None)**: tag

Example

```python
    lookup.send_csv(config['file'], headers=['KEY', 'COLOR', 'HEX'], key=config['lkey'])
```
    
Complete example

````python
conf = Configuration()
conf.load_config("./config.json.example", 'sender')
conf.load_config("./config.json.example", 'lookup')
config = conf.get()
con = Sender.from_dict(config)
lookup = Lookup(name=config['name'], historic_tag=None, con=con)
with open(config['file']) as f:
    line = f.readline()

lookup.send_csv(config['file'], headers=line.rstrip().split(","), key=config['lkey'])

con.socket.shutdown(0)
````

##### Sending data lines to lookup

After initializing the lookup, you can send data to the lookup. There are two ways to do this. 

The first option is to generate a string with the headers structure and then send a control instruction to indicate the start or the end of operation over the lookup. Between those control instructions must be the operations over every row of the lookup.

The header structure is an object list with values and data types of the lookup data.

Example:

```
[{"KEY":{"type":"str","key":true}},{"HEX":{"type":"str"}},{"COLOR":{"type":"str"}}]
```

To facilitate the creation of this string we can call _list_to_headers_ method of _Lookup_ class.

Params

+ lst **(_list_ required)**: column names list of the lookup
+ key **(_string_ required)**: key column name
+ type **(_string_ default: 'str')**: column data type

Example: 

```python
pHeaders = Lookup.list_to_headers(['KEY','HEX', 'COLOR'], 'KEY')
```

With this string we can call _send_control_ method of _Sender_ class to send the control instruction.

Params

+ type **(_string_ required 'START'|'END')**: header type
    - START: start of header
    - END: end of header
+ headers **(_string_ required)**: header structure
+ action **(_string_ required 'FULL'|'INC')**: action type
    - FULL: delete previous lookup data and then add the new
    - INC: add new row to lookup table

Example:

```python
lookup.send_control('START', p_headers, 'INC')
```

The other option is basically the same operations but with less instructions. With _send_headers_ method of _LtLookup_ class we can unify two instructions. 

The relevant difference is that we louse control over data types of lookup data. The data type will be a string.

Params

+ headers **(_list_ default: [] )**: columna name list of lookup 
+ key **(_string_ default 'KEY')**: column name of key
+ event **(_string_ default: 'START')**: header event
    - START: start of header
    - END: end of header
+ headers **(_string_ required)**: header structure
+ action **(_string_ required 'FULL'|'INC')**: action type
    - FULL: delete previous lookup data and then add the new
    - INC: add new row to lookup table

Example:
```python
lookup.send_headers(headers=['KEY', 'HEX', 'COLOR'], key='KEY', event='START', action='FULL')
```

Finally, to send a new row we can use _send_data_line_ method from _LtLooup_ class.

Params

+ key **(_string_ default:'key')**: key value
+ fields **(_list_ default: [])**: values list
+ delete **(_boolean_ default: False)**: row must be deleted

Example:

````python
lookup.send_data_line(key="11", fields=["11", "HEX11", "COLOR11" ])
````

A complete example to send a lookup row is:

````python
conf = Configuration()
conf.load_config("./config.json.example", 'sender')
conf.load_config("./config.json.example", 'lookup')
config = conf.get()
con = Sender.from_dict(config)
lookup = Lookup(name=config['name'], historic_tag=None, con=con)

pHeaders = Lookup.list_to_headers(['KEY','HEX', 'COLOR'], 'KEY')
lookup.send_control('START', pHeaders, 'INC')
lookup.send_data_line(key="11", fields=["11", "HEX11", "COLOR11" ])
lookup.send_control('END', pHeaders, 'INC')

con.socket.shutdown(0)
````

A simplify complete example to send a row of lookup is:

````python
conf = Configuration()
conf.load_config("./config.json.example", 'sender')
conf.load_config("./config.json.example", 'lookup')
config = conf.get()
con = Sender.from_dict(config)
lookup = Lookup(name=config['name'], historic_tag=None, con=con)

lookup.send_headers(headers=['KEY', 'HEX', 'COLOR'], key='KEY', event='START')
lookup.send_data_line(key="11", fields=["11", "HEX12", "COLOR12"], delete=True)
lookup.send_headers(headers=['KEY', 'HEX', 'COLOR'], key='KEY', event='END')

con.socket.shutdown(0)
````

**NOTE:**
- The start and end control instructions should have the list of the names of the columns in the same order in which the lookup was created. 
- Keep in mind that the sockets must be closed at the end

## CLI use
You can use one optional configuration file in the client commands

To send info us the "sender" key, with information to send to Devo.
If you want to add lookup info, you need use the "lookup" key.

A configuration file does not require all the keys, you can pass
the common values: url, port, certificates. After that you can send the tag, the upload file, and
so on, along with the function call.

Both things are combined at runtime, prevailing the values that are sent as 
arguments of the call over the configuration file

Priority order:
1. -c configuration file option: if you use ite, CLI search key, secret and url, or token and url in the file
2. params in CLI call: He can complete values not in configuration file, but does not overrides it
3. Environment vars: if you send the key, secrkey or token in config file or params cli, this option will not be called
4. ~/.devo.json: if you send the key, secrey or token in other ways, this option will not be called
 
**Config file example:** 


```json
  {
    "sender": {
      "address":"devo-relay",
      "port": 443,
      "key": "/devo/certs/key.key",
      "cert": "/devo/certs/cert.crt",
      "chain": "/devo/certs/chain.crt"
    },
    "lookup": {
      "name": "Test lookup",
      "file": "/lookups/lookup.csv",
      "lkey": "KEY"
    }
  }
```

You can see another example in docs/common/config.example.json

#### devo-sender data
`data` command is used to send logs to Devo

```
Usage: devo-sender data [OPTIONS]

  Send to devo

Options:
  -c, --config PATH   Optional JSON File with configuration info.
  -a, --address TEXT  Devo relay address
  -p, --port TEXT     Devo relay address port
  --key TEXT          Devo user key cert file.
  --cert TEXT         Devo user cert file.
  --chain TEXT        Devo chain.crt file.
  --cert_reqs/
  --no-cert_reqs BOOL   Boolean to indicate if the shipment is done using security certificates or not.
  --multiline/
  --no-multiline BOOL Flag for multiline (With break-line in msg). Default is False.
  --type TEXT         Connection type: SSL or TCP
  -t, --tag TEXT      Tag / Table to which the data will be sent in Devo.
  -l, --line TEXT     For shipments of only one line, the text you want to
                      send.
  -f, --file TEXT     The file that you want to send to Devo, which will
                      be sent line by line.
  -h, --header TEXT   This option is used to indicate if the file has headers
                      or not, they will not be send.
  --help              Show help message and exit.
```

Examples
```
#Send test line to table "test.drop.ltsender"
devo-sender data -c ~/certs/config.json

#Send line to table "unknown.unknown"
devo-sender data -c ~/certs/config.json -l "True Survivor - https://www.youtube.com/watch?v=ZTidn2dBYbY"

#Send all file malware.csv (With header) to table "my.app.test.malware"
devo-sender data -c ~/certs/config.json -t my.app.test.films -f "/SecureInfo/my-favorite-disney-films.csv" -h True

#Send file malware.csv (Without header) to table "my.app.test.malware" without config file, using the call to put all info directly
devo-sender data -a app.devo.com -p 10000 --key ~/certs/key.key --cert ~/certs/cert.crt --chain ~/certs/chain.crt  -t my.app.test.films -f "/SecureInfo/my-favorite-disney-films.csv" -h True

```

You have example file in the "tests" folder of the project for a simple, and most useful example).
All the values must be at the same level and without "-"


#### devo-sender lookup
`lookup` command is used to send lookups to Devo

```
Usage: devo-sender lookup [OPTIONS]

  Send csv lookups to devo

Options:
  -c, --config PATH      Optional JSON File with configuration info.
  -a, --address TEXT     Devo relay address
  -p, --port TEXT        Devo relay address port
  --key TEXT             Devo user key cert file.
  --cert TEXT            Devo user cert file.
  --chain TEXT           Devo chain.crt file.
  --cert_reqs/
  --no-cert_reqs BOOL   Boolean to indicate if the shipment is done using security certificates or not.
  --type TEXT            Connection type: SSL or TCP
  -n, --name TEXT        Name for Lookup.
  -f, --file TEXT        The file that you want to send to Devo, which
                         will be sent line by line.
  -lk, --lkey TEXT       Name of the column that contains the Lookup key. It 
                         has to be the exact name that appears in the header.
  -d, --delimiter TEXT   CSV Delimiter char.
  -qc, --quotechar TEXT  CSV Quote char.
  --help                 Show this message and exit.
```


Example
```
#Send lookup when all Devo data is in config file
devo-sender lookup -c ~/certs/config.json -n "Test Lookup" -f "~/tests/test_lookup.csv -lk "KEY"
```
