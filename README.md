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

### Pytest

The SDK uses Pytest for testing. This is a powerful tool for testing Python code. Pytest is a much more flexible and powerful tool than the built-in unittest module. It allows more testing functionality through the use of plugins. You can find more information in the [Pytest documentation](https://docs.pytest.org/en/stable/).

Install the testing requirements:

```console
~/projects/devo-python-sdk > pip install -r requirements-test.txt
```

You can run tests from the `tests` folder of SDK

```console
~/projects/devo-python-sdk/tests > pytest
```

Its normal that TCP tests fails in clients or not Devo developers systems.

You can add the option `--cov` to create a coverage report.

```console
~/projects/devo-python-sdk/tests > pytest --cov
```

Check the [pytest-cov documentation](https://pytest-cov.readthedocs.io/) for more details.

The tests are divided into unit and integration tests. The integration tests require either a connection to Devo or to a local server that is launched when testing, so you need to have the environment variables in your system for all the tests that require connection to Devo can work.

To run the unit tests only, you can use the `unit` folder:

```console
~/projects/devo-python-sdk/tests > pytest unit
```

To run the integration tests only, you can use the `integration` folder:

```console
~/projects/devo-python-sdk/tests > pytest integration
```

You can also run the test for just one module. This is a useful feature if you are developing functionality in just one module.

```console
~/projects/devo-python-sdk/tests > pytest unit/test_sender_encoding.py
```

### Contact Us

You can contact with us at _support@devo.com_.

## License

MIT License

(C) 2024 Devo, Inc.

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
