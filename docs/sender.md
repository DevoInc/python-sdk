# Devo Sender
## Overview

This library allows you to send logs or lookups to the Devo platform.

## Features
- Unification in the way of sending data and lookups
- Allows to send real time data
- Logger integration

## Compatibility 
- Tested compatibility between python 2.x and 3.x series
- Unit tests for use in python 2.x and 3.x

## Usage in script

### Sender

Before sending the lookup information it is necessary to initialize the collector configuration


#### Initializing the collector

There are differents ways and types to initialize the collector configuration

Variable descriptions

+ address **(_string_)**: host name to send data
+ port **(_int_)**: port
+ certs_req **(_boolean__)**: indicates if certificate is required
+ key **(_string_)**: key file path
+ cert **(_string_)**: cert file path
+ chain **(_string_)**: chain file path

- With certificates:
	
	```python
    engine_config = SenderConfigSSL(address=SERVER, port=PORT,key=KEY, cert=CERT,chain=CHAIN)
    con = Sender(engine_config)
	```
	
- Without certificates SSL

	```python
    engine_config = SenderConfigSSL(address=SERVER, port=PORT, certs_req=False)
    con = Sender(engine_config)
	```
	
- Without certificates TCP
	
	```python
    engine_config = SenderConfigTCP(address=SERVER, port=PORT)
    con = Sender(engine_config)
	```
	

- From config function - TCP example
  ```python
    con = Sender.from_config({"address": "relayurl", "port": 443, "type": "TCP"})
  ```

- From config function - SSL example
  ```python
    con = Sender.from_config({"address": "relayurl", "port": 443, "key": "/tmp/key.key", "cert": "/tmp/cert.cert", "chain": "/tmp/chain.crt"})
  ```

- From a file

The file must contain a json format structure with the values into _sender_ variable. The variables will depend of certificate type.

This is a example:

```
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

To initialize the collector configuration from a file we need to import **Configuration** class

```python
from devo.common import Configuration

conf = Configuration()
conf.load_json("./config.json.example", 'sender')
config = conf.get()
engine_config = Sender.from_config(config)
```

#### Sending data 

- After we use the configuration class, we will now be able to send events to the collector

```python
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

The default buffer length its _19500_ and you can change with:

```python
con.max_zip_buffer = 19500
```

You can change the default compression level with:

```python
con.compression_level = 6
```

compression_level is an integer from 0 to 9 or -1 controlling the level of compression; 1 (Z_BEST_SPEED) is fastest and produces the least compression, 9 (Z_BEST_COMPRESSION) is slowest and produces the most. 0 (Z_NO_COMPRESSION) is no compression. The default value is -1 (Z_DEFAULT_COMPRESSION). Z_DEFAULT_COMPRESSION represents a default compromise between speed and compression (currently equivalent to level 6).

###Lookup

As with to send events, to create a new lookup or send data to existents lookup table we need to initializate the collector configuration (as you show previously).

In case to initializate the collector configuration from a json file, you must include a new object into _lookup_ variable with the next parameters:

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

After initializing the colletor, you must initializate the lookup class.

+ name **(_string_)**: lookup table name
+ historic_tag **(_boolean_)**: save historical
+ con **(_LtSender_)**: Sender conection

```python
    lookup = Lookup(name=config['name'], historic_tag=None, con=con)
```

##### Send lookup from CSV file

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
conf.load_json("./config.json.example", 'sender')
conf.load_json("./config.json.example", 'lookup')
config = conf.get()
con = Sender.from_config(config)
lookup = Lookup(name=config['name'], historic_tag=None, con=con)
with open(config['file']) as f:
    line = f.readline()

lookup.send_csv(config['file'], headers=line.rstrip().split(","), key=config['lkey'])

con.socket.shutdown(0)
````

##### Sending data line to lookup

After initializing the lookup, you can send data to the lookup. There are two options to do this. 

The first option is to generate a string with the headers structure and then send a control instruction to indicate start or end of operation over the lookup. Between those control instructions must be the operations over every row of the lookup.

The header structure is an object list with values and data types of the lookup data.

Example:

```
[{"KEY":{"type":"str","key":true}},{"HEX":{"type":"str"}},{"COLOR":{"type":"str"}}]
```

To facility the creation of this string we can call _list_to_headers_ method of _Lookup_ class.

Params

+ lst **(_list_ required)**: column names list of the lookup
+ key **(_string_ required)**: key column name
+ type **(_string_ default: 'str')**: column data type

Example: 

```python
pHeaders = Lookup.list_to_headers(['KEY','HEX', 'COLOR'], 'KEY')
```

With this string, now we can call _send_control_ method of _Sender_ class to send the control instruction.

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

The relevant diference is that we lost control over data types of lookup data. The data type will be a string.

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

A complete example to send a row of lookup is:

````python
conf = Configuration()
conf.load_json("./config.json.example", 'sender')
conf.load_json("./config.json.example", 'lookup')
config = conf.get()
con = Sender.from_config(config)
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
conf.load_json("./config.json.example", 'sender')
conf.load_json("./config.json.example", 'lookup')
config = conf.get()
con = Sender.from_config(config)
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

For send info uses the "sender" key, with information to send to Devo.
If you want add lookup info, you need use the "lookup" key.

A configuration file does not have to have all the necessary keys, you can have 
the common values: url, port, certificates. And then send with the call the tag,
 file to upload, etc.

Both things are combined at runtime, prevailing the values that are sent as 
arguments of the call over the configuration file
 
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
`data` command is used to send logs to devo

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
  --certreq/
  --no-certreq BOOL   Boolean to indicate if the shipment is done using security certificates or not.
  --multiline/
  --no-multiline BOOL Flag for multiline (With break-line in msg). Default False.
  --type TEXT         Connection type: SSL or TCP
  -t, --tag TEXT      Tag / Table to which the data will be sent in Devo.
  -l, --line TEXT     For shipments of only one line, the text you want to
                      send.
  -f, --file TEXT     The file that you want to send to Devo, which will
                      be sent line by line.
  -h, --header TEXT   This option is used to indicate if the file has headers
                      or not, not to send them.
  --help              Show this message and exit.
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

You has example file in "tests" folder of devo.sender project for see one simple 
(And most useful example).
All the values are in the same level and without "-"


#### devo-sender lookup
`lookup` command is used to send lookups to devo

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
  --certreq TEXT         Boolean to indicate if the shipment is done using
                         security certificates or not.
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
