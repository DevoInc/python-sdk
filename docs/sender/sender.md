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
    * **url**: us.elb.relay.logtrust.net
    * **port**: 443
 * **EU:**
    * **url**: eu.elb.relay.logtrust.net
    * **port**: 443
 * **VDC:**
    * **url**: es.elb.relay.logtrust.net
    * **port**: 443
You have more information in the official documentation of Devo, [Sending data to Devo](https://docs.devo.com/confluence/ndt/sending-data-to-devo).

#### Differences in use from version 2 to 3:

You have a special README to quickly show the important changes suffered from version 2 to 3

[You can go read it here](sender_v2_to_v3_major_changes.md)


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
  --raw               Send raw events from file when using --file
  --debug/--no-debug  For testing purposes
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
  -c, --config PATH          Optional JSON/Yaml File with configuration info.
  -e, --env TEXT             Use env vars for configuration
  -d, --default TEXT         Use default file for configuration
  -a, --url, --address TEXT  Devo relay address
  -p, --port INTEGER         Devo relay address port
  --key TEXT                 Devo user key cert file.
  --cert TEXT                Devo user cert file.
  --chain TEXT               Devo chain.crt file.
  --sec_level TEXT           Sec level for opensslsocket. Default: None
  --type TEXT                Connection type: SSL or TCP
  -n, --name TEXT            Name for Lookup.
  -ac, --action TEXT         INC or FULL.
  -f, --file TEXT            The file that you want to send to Devo, which
                             will be sent line by line.
  -lk, --lkey TEXT           Name of the column that contains the Lookup key.
                             It has to be the exact name that appears in the
                             header.
  -ak, --akey TEXT           Name of the column that contains the action key
                             with add or delete. It has to be the exact name
                             that appears in the header.
  -d, --delimiter TEXT       CSV Delimiter char.
  -qc, --quotechar TEXT      CSV Quote char.
  --debug / --no-debug       For testing purposes
  --help                     Show this message and exit.
```


Example
```
#Send lookup when all Devo data is in config file
devo-sender lookup -c ~/certs/config.json -n "Test Lookup" -f "~/tests/test_lookup.csv -lk "KEY"
```
