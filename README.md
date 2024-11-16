![License](https://img.shields.io/github/license/DevoInc/python-sdk)
![Wheel](https://img.shields.io/pypi/wheel/devo-sdk)
![Version](https://img.shields.io/pypi/v/devo-sdk)
![Python](https://img.shields.io/pypi/pyversions/devo-sdk)
![Tests](https://github.com/DevoInc/python-sdk/actions/workflows/python-pull-request.yml/badge.svg)


# Devo Python SDK

## Project Overview
This is the SDK to access Devo directly from Python. It can be used to:
- Send events and files to Devo.
- Make queries.
- Manage deferred tasks.

## Prerequisites
The Devo SDK for Python requires:
- Python 3.9+
- Tested compatibility for Python 3.9, 3.10, 3.11, and 3.12.

## Installation Steps
### Installation Using Package Manager
You can install the Devo SDK using `easy_install` or `pip`:
```console
# option 1
easy_install devo-sdk

# option 2
pip install devo-sdk
```

### Manual Installation
Clone the project and use one of the following commands:
```console
# option 3
python setup.py install

# option 4
pip install .

# option 5 - dev option
pip install -e .
```

### Verification
To verify the successful installation, refer to the specific [documentation](docs) or run the SDK tests.

## Documentation
Detailed documentation is available in the _[docs](docs)_ folder:
- [Sender](docs/sender/sender.md)
  - [Data](docs/sender/data.md)
  - [Lookups](docs/sender/lookup.md)
- [Common](docs/common.md)
- API:
  - [API Query](docs/api/api.md)
  - [Task Management](docs/api/task.md)
    - [Destination: Email](docs/api/destination_email.md)
    - [Destination: Redis](docs/api/destination_redis.md)
    - [Destination: S3](docs/api/destination_s3.md)

## Endpoints
### Sender
Choose the endpoint based on your region:
| Region | Endpoint             | Port |
|--------|----------------------|------|
| USA    | collector-us.devo.io | 443  |
| Canada | collector-ca.devo.io | 443  |
| Europe | collector-eu.devo.io | 443  |
| APAC   | collector-ap.devo.io | 443  |

Refer to the [Sending Data to Devo](https://docs.devo.com/space/latest/94652410/Sending%20data%20to%20Devo) documentation for more details.

### API
Choose the API endpoint based on your region:
| Region | Endpoint                               |
|--------|----------------------------------------|
| USA    | <https://apiv2-us.devo.com/search/query> |
| Canada | <https://apiv2-ca.devo.com/search/query> |
| Europe | <https://apiv2-eu.devo.com/search/query> |
| APAC   | <https://api-apac.devo.com/search/query> |

Refer to the [Query API](https://docs.devo.com/space/latest/95128275/Query%20API) documentation for more details.

## Credentials
To use this SDK, you must have an account in [Devo](https://www.devo.com/). See the [Security Credentials](https://docs.devo.com/space/latest/94763701/Security%20credentials) guide for more details.

### Certificates
Administrator users can find the required certificates (Cert, key, and chain) in **Administration** → **Credentials**, X.509 tab.

### API Authorization
Domain API key and API secret credentials are available under **Administration** → **Credentials**, Access Keys tab.

## Testing
The SDK uses Pytest for testing. Install the testing requirements:
```console
pip install -r requirements-test.txt
```

Run the tests:
```console
pytest
```
Use the `--cov` option for coverage reports:
```console
pytest --cov
```

Tests are divided into unit and integration tests:
- **Unit tests**: `pytest unit`
- **Integration tests**: `pytest integration`

## Contributing
See [PyLibs contributing guide](CONTRIBUTING.md). Pull and merge requests are welcome.

## Help and Support
Contact us at support@devo.com.

## License
This project is licensed under the MIT License.
