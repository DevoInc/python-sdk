# Devo Sender v2 to v3

## Main Changes
The main changes of use come in the creation of the Sender object and its configuration in scripts, 
shell client and the configuration files have also undergone some change

#### Variable changes

An important change is that the definition of "address" has changed to make it 
homogeneous with the definition of the sockets of python 3

In the JSON/YAML configuration file or dict object you can continue using:

`"address": "us.injection.devo.example"`
`"port": "443"`

But a tuple is expected in SenderConfigSSL and SenderConfigTCP:

- expect `address = (url, port)`


#### Sender creation

Removed `kwargs` to receive variables in the creation of the Sender, 
being now more closed and clear.

Formerly, to create a sender object from a dictionary in the past you need 
use `Sender.from_config(config)`, now has a more simple:

`Sender(config=config_dict_objet)`


You can use too:

```
from devo.sender import Sender, SenderConfigSSL, SenderConfigTCP

config = SenderConfigSSL = (address=("url", 444), key="key_path", cert="cert_path", chain="chain_path")
con_ssl = Sender(config=config)


config = SenderConfigTCP = (address=("url", 444))
con_tcp = Sender(config=config)
```

In consequence, `Sender.from_config` has been removed, 

These are the new definitions of these classes

```python
class Sender:
    """
    Class that manages the connection to the data collector

    :param config: SenderConfigSSL, SenderConfigTCP or dict object
    :param con_type: TCP or SSL, default SSL, you can pass it in config object too
    :param timeout: timeout for socket
    :param debug: For more info in console/logger output
    :param logger: logger. Default sys.console
    """
    
class SenderConfigTCP:
    """
    Configuration TCP class.

    :param address:(tuple) Server address
    """
    
class SenderConfigSSL:
    """
    Configuration SSL class.

    :param address: (tuple) (Server address, port)
    :param key: (str) key src file
    :param cert:  (str) cert src file
    :param chain:  (str) chain src file
    """
```
