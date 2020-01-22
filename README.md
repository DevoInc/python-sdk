
[![master Build Status](https://travis-ci.com/DevoInc/python-sdk.svg?branch=master)](https://travis-ci.com/DevoInc/python-sdk) [![LICENSE](https://img.shields.io/dub/l/vibe-d.svg)](https://github.com/DevoInc/python-sdk/blob/master/LICENSE)

[![wheel](https://img.shields.io/badge/wheel-yes-brightgreen.svg)](https://pypi.org/project/devo-sdk/) [![version](https://img.shields.io/badge/version-3.2.0-blue.svg)](https://pypi.org/project/devo-sdk/) [![python](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue.svg)](https://pypi.org/project/devo-sdk/)


# Devo Python SDK

This is the SDK to access Devo directly from Python. It can be used to:
* Send events and files to Devo.
* Make queries.
* Manage deferred tasks.

## Requirements

The Devo SDK for Python requires Python 3.5+

## Compatibility 
- Tested compatibility for python 3.5, 3.6 and 3.7

## Quick Start
### Installing the SDK


You can install the Devo SDK by using `easy_install` or `pip`:

    #option 1
    easy_install devo-sdk
    
    #option 2
    pip install devo-sdk


You can use sources files, clonning the project too:

    #option 3
    python setup.py install
    
    #option 4
    pip install .
    
    #option 5 - dev option
    pip install -e .

### Documentation

You has specific documentation in _[docs](docs)_ folder for each part of SDK:
* [Sender](docs/sender/sender.md)
* [Lookups](docs/sender/lookup.md)
* [Common](docs/common.md)
* API:
    * [Api query](docs/api/api.md)
    * [Api tasks management](docs/api/task.md)
        * [Destination: email](docs/api/destination_email.md)
        * [Destination: redis](docs/api/destination_redis.md)
        * [Destination: S3](docs/api/destination_s3.md)


## Contributing
See [PyLibs contributing guide](CONTRIBUTING.md).<br/>
Pull and merge requests are welcome ☺

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

##### API
To perform a request with API, first choose the required endpoint depending on the region your are accessing from:
 * **USA:** 	https://apiv2-us.devo.com/search/query
 * **EU:**   	https://apiv2-eu.devo.com/search/query
 * **VDC:**   	https://apiv2-es.devo.com/search/query

You have more information in the official documentation of Devo, [REST API](https://docs.devo.com/confluence/ndt/api-reference/rest-api) .

## Credentials
To obtain the access credentials necessary to use this SDK, you must have an account in [DEVO](https://www.devo.com/).<br/>
Check the [security credentials](https://docs.devo.com/confluence/ndt/domain-administration/security-credentials) info for more details. 

##### Certificates
You need use a three files (Cert, key and chain) to secure send data to Devo. 
Administrator users can find them in **Administration** → **Credentials**, in the X.509 tab. 

##### API authorization
You can use a domain API key and API secret to sign the request. These are are a pair of credentials that every 
Devo account owns. Administrator users can find them in **Administration** → **Credentials**, in the Access Keys tab. 

## Launch tests
### run_tests script
You can run tests from the main folder of SDK
To launch this script, you need either the environment variables loaded in the system, or the _environment.env_ file in the root of the SDK with the correct values, since to test all the SDK functionalities it is necessary to connect to Devo for the tests of sending and extracting data. You has a example file called _environment.env.example_

Its normal, by the way, TCP tests fails in clients or not Devo developers systems.

```bash
~/projects/devo-python-sdk > python setup.py test 
```

```bash
~/projects/devo-python-sdk > python run_tests.py
```

You can add option "Coverage" for create HTML report about tests.

```bash
~/projects/devo-python-sdk > python run_tests.py --coverage
```


### Run using Unittest command

You can see references in [unittest documentation](https://docs.python.org/3/library/unittest.html)

For commands like:

```bash
python -m unittest discover -p "*.py" 
```

If you launch this command from the root directory of the SDK, you need to have the environment variables in your 
system for all the tests that require connection to Devo can work, not being able to use the environment.env file 
as in the script.


### Contact Us

You can contact with us at _support@devo.com_.

## License
MIT License

(C) 2019 Devo, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the 'Software'), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
