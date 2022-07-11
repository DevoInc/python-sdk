# devo-sender
## Overview

This library allows you to send logs to the Devo platform.

## Features
- Data and lookups sending merged in one procedure
- Allows to send real time data
- Logger integration and logging handler capacity for Sender
- Send lookups to Devo

You have info about usage in scripts here:
- [Data](data.md)
- [Lookups](lookup.md)

## Endpoints
##### Sender
To send data with Devo SDK, first choose the required endpoint depending on the region your are accessing from:

| Region 	| Endpoint                  	| Port 	|
|--------	|---------------------------	|------	|
| USA    	| us.elb.relay.logtrust.net 	| 443  	|
| Europe 	| eu.elb.relay.logtrust.net 	| 443  	|
| VDC    	| es.elb.relay.logtrust.net 	| 443  	|
    
You have more information in the official documentation of Devo, [Sending data to Devo](https://docs.devo.com/confluence/ndt/sending-data-to-devo).

#### Differences in use from version 2 to 3:

You have a special README to quickly show the important changes suffered from version 2 to 3

[You can go read it here](sender_v2_to_v3_major_changes.md)

## CLI usages
#### devo-sender data
This command is used to send logs to Devo

```
Usage: devo-sender data [OPTIONS]

  Send to devo

Options:
  -c, --config PATH             Optional JSON/Yaml File with configuration
                                info.

  -a, --address TEXT            Devo relay address
  -p, --port TEXT               Devo relay address port
  --key TEXT                    Devo user key cert file.
  --cert TEXT                   Devo user cert file.
  --chain TEXT                  Devo chain.crt file.
  --sec_level INTEGER           Sec level for opensslsocket. Default: None
  --verify_mode INTEGER         Verify mode for SSL Socket. Default: SSL
                                default.You need use int "0" (CERT_NONE), "1"
                                (CERT_OPTIONAL) or "2" (CERT_REQUIRED)

  --check_hostname BOOLEAN      Verify cert hostname. Default: True
  --multiline / --no-multiline  Flag for multiline (With break-line in msg).
                                Default False

  --type TEXT                   Connection type: SSL or TCP
  -t, --tag TEXT                Tag / Table to which the data will be sent in
                                Devo.

  -l, --line TEXT               For shipments of only one line, the text you
                                want to send.

  -f, --file TEXT               The file that you want to send to Devo, which
                                will be sent line by line.

  -h, --header BOOLEAN          This option is used to indicate if the file
                                has headers or not, not to send them.

  --raw                         Send raw events from a file when using --file
  --debug / --no-debug          For testing purposes
  --zip / --no-zip              For testing purposes
  --buffer INTEGER              Buffer size for zipped data.
  --compression_level INTEGER   Compression level for zipped data. Read readme
                                for more info

  -e, --env BOOLEAN             Use env vars for configuration
  -d, --default BOOLEAN         Use default file for configuration
  --help                        Show this message and exit.
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
  -c, --config PATH               Optional JSON/Yaml File with configuration
                                  info.

  -e, --env BOOLEAN               Use env vars for configuration
  -d, --default BOOLEAN           Use default file for configuration
  -a, --url, --address TEXT       Devo relay address
  -p, --port INTEGER              Devo relay address port
  --key TEXT                      Devo user key cert file.
  --cert TEXT                     Devo user cert file.
  --chain TEXT                    Devo chain.crt file.
  --sec_level INTEGER             Sec level for opensslsocket. Default: None
  --verify_mode INTEGER           Verify mode for SSL Socket. Default: SSL
                                  default.You need use int "0" (CERT_NONE),
                                  "1" (CERT_OPTIONAL) or "2" (CERT_REQUIRED)

  --check_hostname BOOLEAN        Verify cert hostname. Default: True
  --type TEXT                     Connection type: SSL or TCP
  -n, --name TEXT                 Name for Lookup.
  -ac, --action TEXT              INC or FULL.
  -f, --file TEXT                 The file that you want to send to Devo,
                                  which will be sent line by line.

  -lk, --lkey TEXT                Name of the column that contains the Lookup
                                  key. It has to be the exact name that
                                  appears in the header.

  -dk, --dkey TEXT                Name of the column that contains the
                                  action/delete key with "add" or "delete".It
                                  has to be the exact name that appears in the
                                  header.

  -dt, --detect-types / -ndt, --no-detect-types
                                  Detect types of fields. Default: False
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
1. -c configuration file option: if you use it, params in the file
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
      "chain": "/devo/certs/chain.crt",
      "verify_config": true
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
  verify_config: true
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
