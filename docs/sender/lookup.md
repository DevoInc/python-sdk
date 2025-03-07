# Devo sender to send lookups

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Devo sender to send lookups](#devo-sender-to-send-lookups)
  - [Overview](#overview)
  - [Script usage](#script-usage)
    - [Sending lookup data with your own script](#sending-lookup-data-with-your-own-script)
      - [Send lookups from CSV file](#send-lookups-from-csv-file)
      - [Double quotes in the field value](#double-quotes-in-the-field-value)

<!-- /code_chunk_output -->

## Overview

This library allows you to send lookups to the Devo platform.

You have two types of uses, in script (This doc) or [send using shell](sender.md#devo-sender-lookup)

You need to know how work [Sender](sender.md) and [Data](data.md) to use Lookup functions in script, but not for shell

## Script usage

Just like the send events case, to create a new lookup or send data to existent lookup table we need to initialize the collector configuration.

In case to initialize the collector configuration from a json/yaml file, you must include a new object into the _lookup_ variable with the new parameters or add in the CLI flags:

Example:

```
{   
    sender": {
        ...
    },
    "lookup": {
        "name": "Test_Lookup_of_180306_02",
        "file": "test_lookup.csv",
        "lkey": "KEY",
        "escape_quotes": true
    }
}
```

You can see more examples below

### Sending lookup data with your own script

After initializing the lookup, you can send data to the lookup. There are two ways to do this.

The first option is to generate a string with the headers structure and then send a control instruction to indicate the start or the end of operation over the lookup. Between those control instructions must be the operations over every row of the lookup.

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
+ types **(_list_ optional')**: list of type:  with types of columns in order

Accepted types:

- String -> "str"
- Integer -> "int" (default int type: int8)
- Integer4 -> "int4"
- Integer8 -> "int8"
- Float -> "float"
- Boolean -> "bool"
- IP -> "ip4"

Example:

```python
from devo.sender import Lookup
pHeaders = Lookup.list_to_headers( 
                                   headers=list, #List with all headers names
                                   type_of_key="str",
                                   key=None,  #Name of the Key
                                   key_index=None, #Or index of key in headers list, you can use whatever you want
                                   types=list 
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
lookup.send_control(event='START', headers=["id", "name", "email"], action='INC')
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

+ key_index **(_string_ optional default: None)**: or key index in list fields
+ fields **(_list_ default: [])**: values list: can be str, int, float and bool
+ delete **(_boolean_ default: False)**: row must be deleted

Example:

````python
lookup.send_data_line(key_index=0, fields=["11", "HEX11", "COLOR11" ])
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
lookup.send_data_line(key_index=0, fields=["11", "HEX11", "COLOR11" ])
lookup.send_data_line(key_index=0, fields=[22, "HEX22", "COLOR22"])
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
lookup.send_data_line(key_index=0, fields=["11", "HEX12", "COLOR12"], delete=True)
lookup.send_headers(headers=['KEY', 'HEX', 'COLOR'], key='KEY', event='END', action="INC")

con.socket.shutdown(0)
````

**NOTE:**

- The start and end control instructions should have the list of the names of the columns in the same order in which the lookup was created.
- Keep in mind that the sockets must be closed at the end
- The lookups are sent to Devo and a process running in the background loads and distributes them. It can take a few minutes to have the lookup available.

#### Send lookups from CSV file

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
+ types **(_list_ default: None)**: List with type of fields
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

You can use config file to send types list:

```
{
 'lookup' : {
    'types': ["int", "str", "int4", "bool", "int8"]
    ....
 }
}
```

#### Double quotes in the field value

Any double quotes inside the field value can cause trouble when sending the lookup if this is not escaped.
An example of this case can be seen below:

```python
lookup.send_data_line(key_index=0, fields=["11", 'double quotes must escaped"'])
```

That lookup creation will fail because that double quote will be interpreted as a field termination and  the number of fields for that row will unmatch the corresponding number of columns. To avoid this, add `"escape_quotes": true` to the lookup configuration file and `escape_quotes=True` to the `Lookup` constructor. Below, an example for the constructor is shown:

```python
lookup = Lookup(name=self.lookup_name, historic_tag=None, con=con, escape_quotes=True)
```

To see an example for the lookup configuration please refer to the one shown at the start of the document.

This will escape ALL double quotes in the field value by adding a second double quote to it.

The default behavior is to NOT escape any double quotes.

#### New line chars in the field value

Any new line char inside the field value can cause trouble when creating the lookup if this is not escaped.
An example of this case can be seen below:

```python
lookup.send_data_line(key_index=0, fields=["11", 'new lines\n must be escaped'])
```

That lookup creation will fail because that new line char quote may create null fields. To avoid this, add `"escape_newline": true` to the lookup configuration file and `escape_newline=True` to the `Lookup` constructor. Below, an example for the constructor is shown:

```python
lookup = Lookup(name=self.lookup_name, historic_tag=None, con=con, escape_newline=True)
```

To see an example for the lookup configuration please refer to the one shown at the start of the document.

This will escape ALL new line chars in the field value by adding a second backslash to it.

The default behavior is to NOT escape any new line chars.