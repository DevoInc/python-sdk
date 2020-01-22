# Devo sender to send lookups

Just like the send events case, to create a new lookup or send data to existent 
lookup table we need to initialize the collector configuration 
(as previously shown).

In case to initialize the collector configuration from a json/yaml file, you must include a new 
object into the _lookup_ variable with the new parameters or add in the CLI flags:

Example:

```
{   sender": {
        ...
    },
    "lookup": {
        "name": "Test_Lookup_of_180306_02",
        "file": "test_lookup.csv",
        "lkey": "KEY"
    }
}
```

You can see more examples below

##### Sending lookup data with your own script

After initializing the lookup, you can send data to the lookup. There are two ways to do this. 

The first option is to generate a string with the headers structure and then send a control
 instruction to indicate the start or the end of operation over the lookup. 
 Between those control instructions must be the operations over every row of the lookup.

The header structure is an object list with values and data types of the lookup data.

Example:

```
[{"KEY":{"type":"str","key":true}},{"HEX":{"type":"str"}},{"COLOR":{"type":"str"}}]
```

To facilitate the creation of this string we can call _list_to_headers_ method of _Lookup_ class.

Params

+ headers **(_list_ required)**: column names list of the lookup
+ type_of_key **(_string_ optional)**: specify a concrete type for the key (Default string)
+ key **(_string_ optional)**: name of key
+ key_index **(_string_ optional)**: index of key. You can use this or key
+ types **(_dict_ optional')**: dict of type: {"header_name": "header_type", "head....} with types of columns

Example: 

```python
from devo.sender import Lookup
pHeaders = Lookup.list_to_headers( 
                                   headers=list, #List with all headers names
                                   type_of_key="str",
                                   key=None,  #Name of the Key
                                   key_index=None, #Or index of key in headers list, you can use whatever you want
                                   types=dict #Dict with {"headername": "hadertype", "headern....}
                                  )
```

With this string we can call _send_control_ method of _Sender_ class to send the control instruction.

Params

+ event **(_string_ required 'START'|'END')**: header type
    - START: start of header
    - END: end of header
+ headers **(_string_ required)**: header structure
+ action **(_string_ required 'FULL'|'INC')**: action type
    - FULL: delete previous lookup data and then add the new
    - INC: add new row to lookup table

Example:

```python
lookup.send_control(event='START', headers=p_headers, action='INC')
```

The other option is basically the same operations but with less instructions:
You can use _send_headers_ method of _LtLookup_ class we can unify _list_to_headers_ + _send_control_.


_send_headers_ Params
+ headers **(_list_ default: [] )**: column name list of lookup 
+ key **(_string_ default 'KEY')**: column name of key
+ key_index **(_string_ default 'KEY')**: column name of key
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

+ key **(_string_ optional default: None)**: key value
+ key_index **(_string_ optional default: None)**: or key index in list fields
+ fields **(_list_ default: [])**: values list
+ delete **(_boolean_ default: False)**: row must be deleted

Example:

````python
lookup.send_data_line(key="11", fields=["11", "HEX11", "COLOR11" ])
````

A complete example to send a lookup row is:

````python
from devo.common import Configuration
from devo.sender import Sender, Lookup

conf = Configuration(path="./config.json.example")
con = Sender(config=conf.get("sender"))
lookup = Lookup(name=conf.get('lookup').get('name', "default"), historic_tag=None, con=con)
pHeaders = Lookup.list_to_headers(headers=['KEY','HEX', 'COLOR'], key='KEY')
lookup.send_control(event='START', headers=pHeaders, action='INC')
# You can use key value
lookup.send_data_line(key="11", fields=["11", "HEX11", "COLOR11" ])
# Or you can use key_index (Position in list)
lookup.send_data_line(key_index=0, fields=["22", "HEX22", "COLOR22" ])
lookup.send_control(event='END', headers=pHeaders, action='INC')

con.socket.shutdown(0)
````

A simplify complete example to send a row of lookup is:

````python
from devo.common import Configuration
from devo.sender import Sender, Lookup

conf = Configuration()
conf.load_config("./config.json.example", 'sender')
conf.load_config("./config.json.example", 'lookup')
con = Sender(config=conf.get("sender"))
lookup = Lookup(name=conf.get('name', "default"), historic_tag=None, con=con)

lookup.send_headers(headers=['KEY', 'HEX', 'COLOR'], key='KEY', event='START', action="INC")
lookup.send_data_line(key="11", fields=["11", "HEX12", "COLOR12"], delete=True)
lookup.send_headers(headers=['KEY', 'HEX', 'COLOR'], key='KEY', event='END', action="INC")

con.socket.shutdown(0)
````

**NOTE:**
- The start and end control instructions should have the list of the names of the columns in the same order in which the lookup was created. 
- Keep in mind that the sockets must be closed at the end



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
+ action **(_string_ default: None)**: FULL (Delete old if exist) or INC (Update if exist), action for the lookup
+ action_field **(_string_ default: None)**: field name (Name in header) with the field of action for the row (add or delete)
+ types **(_string_ default: None)**: Dict with type of fields
+ detect_types **(_string_ default: False)**: Detect types of fields reading first line

Example

```python
    lookup.send_csv(config['file'], headers=['KEY', 'COLOR', 'HEX'], key=config['lkey'])
```
    
Complete example

````python
from devo.common import Configuration
from devo.sender import Sender, Lookup
conf = Configuration("./config.json.example")
con = Sender(config=conf.get("sender"))
lookup = Lookup(name=conf.get('lookup').get('name', "default"), historic_tag=None, con=con)
lookup.send_csv(path=conf.get('lookup').get('file', "example.csv"), 
                has_header=True, key=conf.get('lkey', "ID"))
con.socket.shutdown(0)
````


## CLI use
You can use one optional configuration file in the client commands

#### devo-sender lookup
`lookup` command is used to send lookups to Devo

```
Usage: devo-sender lookup [OPTIONS]

  Send csv lookups to devo

Options:
  -c, --config PATH               Optional JSON/Yaml File with configuration
                                  info.
  -e, --env TEXT                  Use env vars for configuration
  -d, --default TEXT              Use default file for configuration
  -a, --url, --address TEXT       Devo relay address
  -p, --port INTEGER              Devo relay address port
  --key TEXT                      Devo user key cert file.
  --cert TEXT                     Devo user cert file.
  --chain TEXT                    Devo chain.crt file.
  --sec_level TEXT                Sec level for opensslsocket. Default: None
  --type TEXT                     Connection type: SSL or TCP
  -n, --name TEXT                 Name for Lookup.
  -ac, --action TEXT              INC or FULL.
  -f, --file TEXT                 The file that you want to send to Devo,
                                  which will be sent line by line.
  -lk, --lkey TEXT                Name of the column that contains the Lookup
                                  key. It has to be the exact name that
                                  appears in the header.
  -ak, --akey TEXT                Name of the column that contains the action
                                  key with add or delete. It has to be the
                                  exact name that appears in the header.
  -dt, --detect-types / -ndt, --no-detect-types
                                  Detect types of fields.
  -d, --delimiter TEXT            CSV Delimiter char.
  -qc, --quotechar TEXT           CSV Quote char.
  --debug / --no-debug            For testing purposes
  --help                          Show this message and exit.
```


Example
```
#Send lookup when all Devo data is in config file
devo-sender lookup -c ~/certs/config.json -n "Test Lookup" -f "~/tests/test_lookup.csv -lk "KEY"
```


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
```yaml
sender:
  address: "devo-relay"
  port: 443
  key: "/devo/certs/key.key"
  cert: "/devo/certs/cert.crt"
  chain: "/devo/certs/chain.crt"
lookup: 
  name: "Test lookup"
  file: "/lookups/lookup.csv"
  lkey: "ID"
  types:
    id: "int"
    name: "str"
    building: "str"
    subnet: "192.168.17.1"
```

You can see another example in docs/common/config.example.json
