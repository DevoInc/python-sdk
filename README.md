![License](https://img.shields.io/github/license/DevoInc/python-sdk)
![Wheel](https://img.shields.io/pypi/wheel/devo-sdk)
![Version](https://img.shields.io/pypi/v/devo-sdk)
![Python](https://img.shields.io/pypi/pyversions/devo-sdk)
![Tests](https://github.com/DevoInc/python-sdk/actions/workflows/python-pull-request.yml/badge.svg)

# Devo Python SDK

This is the SDK to access Devo directly from Python. It can be used to:

- Send events and files to Devo.
- Make queries.
- Manage deferred tasks.

## Requirements

The Devo SDK for Python requires Python 3.8+

## Compatibility

- Tested compatibility for python 3.8 and 3.9

## Quick Start

### Installing the SDK

You can install the Devo SDK by using `easy_install` or `pip`:

```console
#option 1
easy_install devo-sdk

#option 2
pip install devo-sdk
```

You can use sources files, cloning the project too:

```console
#option 3
python setup.py install

#option 4
pip install .

#option 5 - dev option
pip install -e .
```

### Documentation

There is specific documentation in the _[docs](docs)_ folder for each part of SDK:

- [Sender](docs/sender/sender.md)
  - [Data](docs/sender/data.md)
  - [Lookups](docs/sender/lookup.md)
- [Common](docs/common.md)
- API:
  - [Api query](docs/api/api.md)
  - [Api tasks management](docs/api/task.md)
    - [Destination: email](docs/api/destination_email.md)
    - [Destination: redis](docs/api/destination_redis.md)
    - [Destination: S3](docs/api/destination_s3.md)

## Contributing

See [PyLibs contributing guide](CONTRIBUTING.md).<br/>
Pull and merge requests are welcome ☺

## Endpoints

### Sender

To send data with Devo SDK, first choose the required endpoint depending on the region your are accessing from:

| Region | Endpoint             | Port |
|--------|----------------------|------|
| USA    | collector-us.devo.io | 443  |
| Canada | collector-ca.devo.io | 443  |
| Europe | collector-eu.devo.io | 443  |
| APAC   | collector-ap.devo.io | 443  |

You have more information in the official documentation of Devo, [Sending data to Devo](https://docs.devo.com/space/latest/94652410/Sending%20data%20to%20Devo).

### API

To perform a request with API, first choose the required endpoint depending on the region your are accessing from:

| Region | Endpoint                               |
|--------|----------------------------------------|
| USA    | <https://apiv2-us.devo.com/search/query> |
| Canada | <https://apiv2-ca.devo.com/search/query> |
| Europe | <https://apiv2-eu.devo.com/search/query> |
| APAC   | <https://api-apac.devo.com/search/query> |

You have more information in the official documentation of Devo, [REST API](https://docs.devo.com/space/latest/95128275/Query%20API).

## Credentials

To obtain the access credentials necessary to use this SDK, you must have an account in [DEVO](https://www.devo.com/).

Check the [security credentials](https://docs.devo.com/space/latest/94763701/Security%20credentials) info for more details.

### Certificates

You need use a three files (Cert, key and chain) to secure send data to Devo.
Administrator users can find them in **Administration** → **Credentials**, in the X.509 tab.

### API authorization

You can use a domain API key and API secret to sign the request. These are are a pair of credentials that every
Devo account owns. Administrator users can find them in **Administration** → **Credentials**, in the Access Keys tab.

## Launch tests

### run_tests script

You can run tests from the main folder of SDK
To launch this script, you need either the environment variables loaded in the system, or the _environment.env_ file in the root of the SDK with the correct values, since to test all the SDK functionalities it is necessary to connect to Devo for the tests of sending and extracting data. There is an example file called _environment.env.example_

Its normal, by the way, TCP tests fails in clients or not Devo developers systems.

```console
~/projects/devo-python-sdk > python setup.py test
```

```console
~/projects/devo-python-sdk > python run_tests.py
```

You can add option "Coverage" for create HTML report about tests.

```console
~/projects/devo-python-sdk > python run_tests.py --coverage
```

You can also run the test for just one module. This is a useful feature if you are developing functionality in just one module.

```console
~/projects/devo-python-sdk > python run_tests.py -m SENDER_CLI
```

You can also exclude one or several tests with `-M` parameter:

```console
~/projects/devo-python-sdk > python run_tests.py -M SENDER_CLI,API_CLI
```

Using the --help flag prints the available modules to use:

```console
~/projects/devo-python-sdk > python run_tests.py --help
usage: run_tests.py [-h] [--coverage [COVERAGE]] [-m [MODULE]]

optional arguments:
  -h, --help            show this help message and exit
  --coverage [COVERAGE]
                        Generate coverage
  -m [MODULES], --modules [MODULES]
                        Run tests for selected modules: API_CLI, API_QUERY, API_TASKS, API_ERRORS, API_PARSER_DATE,
                        API_PROCESSORS, API_KEEPALIVE, COMMON_CONFIGURATION, COMMON_DATE_PARSER, SENDER_CLI, SENDER_CSV,
                        SENDER_NUMBER_LOOKUP, SENDER_SEND_DATA, SENDER_SEND_LOOKUP
  -M [EXCLUDE_MODULES], --exclude-modules [EXCLUDE_MODULES]
                        Exclude tests for modules: API_CLI, API_QUERY, API_TASKS, API_ERRORS, API_PARSER_DATE,
                        API_PROCESSORS, API_KEEPALIVE, COMMON_CONFIGURATION, COMMON_DATE_PARSER, SENDER_CLI, SENDER_CSV,
                        SENDER_NUMBER_LOOKUP, SENDER_SEND_DATA, SENDER_SEND_LOOKUP
```

- API_CLI: API Command-line interface tests.
- API_QUERY: Query API tests.
- API_TASKS: Task API tests.
- API_ERRORS: Managing of API Errors tests.
- API_PARSER_DATE: Parsing of dates in API tests.
- API_PROCESSORS: Response processors in API tests.
- API_KEEPALIVE: Keep Alive functionality in API tests.
- COMMON_CONFIGURATION: Configuration tests.
- COMMON_DATE_PARSER: Date parser tests.
- SENDER_CLI: Lookup command-line interface tests.
- SENDER_CSV: Lookup uploading through CSV tests.
- SENDER_NUMBER_LOOKUP: Numbers in lookup tests
- SENDER_SEND_DATA: Data sending tests.
- SENDER_SEND_LOOKUP: Lookup sending tests.

### Run using Unittest command

You can see references in [unittest documentation](https://docs.python.org/3/library/unittest.html)

For commands like:

```console
python -m unittest discover -p "*.py"
```

If you launch this command from the root directory of the SDK, you need to have the environment variables in your
system for all the tests that require connection to Devo can work, not being able to use the environment.env file
as in the script.

### Contact Us

You can contact with us at _support@devo.com_.

## License

MIT License

(C) 2023 Devo, Inc.

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
