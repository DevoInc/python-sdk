# Devo sender to send data

## Usage in script
Before sending the data it is necessary to initialize the collector configuration

#### Initializing the collector

There are different ways (and types) to initialize the collector configuration

Variable descriptions

+ config **(_SenderConfigSSL_, _SenderConfigTCP_ or _dict_)**: address, port, keypath, chainpath, etc
+ con_type **(_string_)**: TCP or SSL, default SSL, you can pass it in config object too
+ timeout **(_int_)**: timeout for socket
+ debug **(_bool_)**: True or False, for show more info in console/logger output
+ logger **(_string_)**: logger. Default sys.console


Class SenderConfigSSL accept various types of certificates, you has:

+ address **(_tuple_)**: (Server address, port)
+ key **(_str_)**: key src file
+ cert **(_str_)**: cert src file
+ chain **(_str_)**: chain src file
+ pkcs **(_dict_)**: (path: pfx src file, password: of cert)
+ sec_level **(_int_)**: Security level to openssl launch


You can use the collector in some ways:

- With certificates:
	
```python
from devo.sender import SenderConfigSSL, Sender
engine_config = SenderConfigSSL(address=(SERVER, PORT), 
                                key=KEY, cert=CERT,chain=CHAIN)
con = Sender(engine_config)
```

or 

```python
from devo.sender import SenderConfigSSL, Sender
engine_config = SenderConfigSSL(address=(SERVER, PORT), 
                                pkcs={"path": "tmp/mycert.pfx",
                                      "password": "certpassword"})
con = Sender(engine_config)
```
	
- Without certificates SSL

```python
from devo.sender import SenderConfigSSL, Sender
engine_config = SenderConfigSSL(address=(SERVER, PORT))
con = Sender(engine_config)
```
	
- Without certificates TCP
	
```python
from devo.sender import SenderConfigTCP, Sender
engine_config = SenderConfigTCP(address=(SERVER, PORT))
con = Sender(engine_config)
```
	

- From dict - TCP example
```python
from devo.sender import Sender
con = Sender(config={"address": "collector", "port": 443, "type": "TCP"})
```

- From dict - SSL example
```python
from devo.sender import Sender
con = Sender(config={"address": "collector", "port": 443, 
                     "key": "/tmp/key.key", "cert": "/tmp/cert.cert", 
                     "chain": "/tmp/chain.crt"})
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
	        "chain": "/devo/certs/chain.crt",
	        "type": "SSL"
	    },
}
```

This is a yaml example:

```yaml
sender:
  address: "devo-relay"
  port: 443
  key: "/devo/certs/key.key"
  cert: "/devo/certs/cert.crt"
  chain: "/devo/certs/chain.crt"
  type: "SSL"
```

To initialize the collector configuration from a file we need to import **Configuration** class

```python
from devo.common import Configuration
from devo.sender import Sender

conf = Configuration("./config.json.example", 'sender')
con = Sender(config=conf)
```

#### Sending data 

After we use the configuration class, we will now be able to send events to the collector

- send logs to the collector,

```python
con.send(tag="test.drop.actors", msg='Hasselhoff')
```
- Send raw log to collector

```python
con.send_raw('<14>Jan  1 00:00:00 Nice-MacBook-Pro.local'
             'test.drop.actors: Testing this cool tool')
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
 
 
## CA_MD_TOO_WEAK - Openssl security level
Or CA signature digest algorithm too weak its a error with news versions of openssl>=1.1.0
If you have problem with your certificates of Devo and devo-sdk you with this error you can add flag `sec_level=0` 
on your configuration, SenderConfigSSL or CLI:

```python
from devo.sender import SenderConfigSSL

engine_config = SenderConfigSSL(address=("devo.collector", 443),
                                key="key.key", cert="cert.crt",
                                chain="chain.crt", sec_level=0)
```

#### Openssl security levels:

- Level 0: 
    - Everything is permitted. This retains compatibility with previous versions of OpenSSL.
- Level 1: 
    - The security level corresponds to a minimum of 80 bits of security. Any parameters offering below 80 bits of security are excluded. As a result RSA, DSA and DH keys shorter than 1024 bits and ECC keys shorter than 160 bits are prohibited. All export ciphersuites are prohibited since they all offer less than 80 bits of security. SSL version 2 is prohibited. Any ciphersuite using MD5 for the MAC is also prohibited.
- Level 2: 
    - Security level set to 112 bits of security. As a result RSA, DSA and DH keys shorter than 2048 bits and ECC keys shorter than 224 bits are prohibited. In addition to the level 1 exclusions any ciphersuite using RC4 is also prohibited. SSL version 3 is also not allowed. Compression is disabled.
- Level 3: 
    - Security level set to 128 bits of security. As a result RSA, DSA and DH keys shorter than 3072 bits and ECC keys shorter than 256 bits are prohibited. In addition to the level 2 exclusions ciphersuites not offering forward secrecy are prohibited. TLS versions below 1.1 are not permitted. Session tickets are disabled.
- Level 4: 
    - Security level set to 192 bits of security. As a result RSA, DSA and DH keys shorter than 7680 bits and ECC keys shorter than 384 bits are prohibited. Ciphersuites using SHA1 for the MAC are prohibited. TLS versions below 1.2 are not permitted.
- Level 5: 
    - Security level set to 256 bits of security. As a result RSA, DSA and DH keys shorter than 15360 bits and ECC keys shorter than 512 bits are prohibited.



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
                                
con = Sender.for_logging(config=engine_config, tag="my.app.test.logger")
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


## CLI use
You can use shell to send data without creation of scripts


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
