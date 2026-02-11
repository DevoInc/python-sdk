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

> [!WARNING]  
> Right now the upload of lookups functionality is based on the `my.lookup.data` and `my.lookup.control` tables. 
> This method is deprecated on the Devo backend, and it will be discontinued on 1st January 2026.
> As an alternative, you can use the Lookups API: [Lookups API Documentation](https://docs.devo.com/space/latest/127500289/Lookups+API).
> There is a [developer guide](docs/sender/api_lookup_guide.md) in documentation.

## Requirements

The Devo SDK for Python requires Python 3.9+

## Compatibility

- Tested compatibility for python 3.9, 3.10, 3.11, 3.12 and 3.13

## Quick Start

### Installing the SDK

You can install the Devo SDK by using `easy_install` or `pip`:

```console
# option 1
easy_install devo-sdk

# option 2
pip install devo-sdk
```

You can use sources files, cloning the project too:

```console
# option 3
python setup.py install

# option 4
pip install .

# option 5 - dev option
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

The SDK uses [Pytest](https://docs.pytest.org/en/stable/) for testing. Install the package and testing requirements, then run tests from the **project root**:

```console
pip install -e .
pip install -r requirements-test.txt
```

**Run all tests:**

```console
python -m pytest tests/
```

**Run only unit tests:**

```console
python -m pytest tests/unit/
```

**Run only integration tests:**

```console
python -m pytest tests/integration/
```

**Run a single test file:**

```console
python -m pytest tests/unit/test_sender_encoding.py
```

**Run with coverage report:**

```console
python -m pytest tests/ --cov
```

See the [pytest-cov documentation](https://pytest-cov.readthedocs.io/) for coverage options.

Integration tests need either a connection to Devo or a local server started by the test run; some tests also require environment variables (e.g. `DEVO_API_KEY`, `DEVO_API_SECRET`) or certificate paths. It is normal for integration tests that require Devo credentials or remote certs to be skipped or fail when those are not configured.

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
