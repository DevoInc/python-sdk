# Devo Sender v2 to v3

## Main Changes
The Client object has a lot of changes, we can resume this in 3 important points

#### Variable changes

An important change is that the definition of "url" has changed to make it 
homogeneous with the definition of the sockets of python 3 and the rest of the sdk

`url` is now `address`, you can see more below

## Client init

**Client** class dont have `*kwargs` too, and we separate "config" and "important things".
Client params are now:

* address: endpoint in python tuple mode -> (address, port)
* auth: object with auth params (key and secret, token or jwt)
    * for example -> `auth={"key": "qwertyasdf", "secret": "zxcvbasdfg"}`
* config: config class for Client and queries
* retries: number of retries for a query
* timeout: timeout of socket (Important if you make huge queries)

The **ClientConfig** class is the one that has the rest of the values that we were used to 

* processor: processor for response, default is None
* response: format of response
* destination: Destination options
* stream: Stream queries or not


## Client creation from dict

`Client.from_config()` -> `Client(config=dict_config)`
 
Formerly used to create a client object from a dictionary, now has a more easy way