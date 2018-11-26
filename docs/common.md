# Devo Common library
## Overview
This library add utilities for other packages.

## Features

- Unification in the way of treating date formats
- Unification in the way of treating configuration files
- Logging functions
- Custom memoize def


#### Config files

You can use config files in JSON and YAML to create Sender and Api objects, loading files with:

```python
from devo.common import Configuration

config = Configuration()

#:param path: Path to the json file
#:param section: Section of the file if it have one
#    :return: Returns a reference to the instance object
config.load_config("path_to_file.[yml|yaml|json]")
config_dict = config.get()
```

You has extra param `section` in `load_config` function for load only one subsection of file

Here has two examples of config files:

```yaml
api:
  key: "MyAPIkeytoaccessdevo"
  secret: "MyAPIsecrettoaccessdevo"
  url: "https://api-us.logtrust.com/search/query"
```


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


#### Date Formats
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


#### Standard Devo configuration file

Devo Common contains the [`Configuration`](common/generic/configuration.py) 
class to read JSON or YAML configuration files 
and automix an array with the file.

You can see in several Devo libraries that the CLI allows the reading of a 
config.json/config.yaml file, they all use this class to load them, and in each of the 
libraries you can find the format they use, in addition to examples of use in 
this class tests.

