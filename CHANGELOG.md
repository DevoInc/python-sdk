# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [5.1.9] - 2024-02-06

### Added

- Tests for encoding of messages in Sender.

### Changed

- UFT-8 encoding with "replace" is now used by default in Sender.

## [5.1.8] - 2024-01-10

### Added

- Added Code of Conduct.

### Changed

- Restrict insecure TLS versions in Sender and API clients to TLSv1.2 and TLSv1.3.
- Remove disclosing information in messages about keepalive token.
- Fix incorences in documentation about using `url` and `address` interchangeably.
- `certifi` dependency upgraded from `certifi~=2023.7.22` to `certifi~=2023.11.17`
- `cryptography` dependency upgraded from `cryptography~=41.0.5` to `cryptography~=41.0.7`
- `pipdeptree` dependency upgraded from `pipdeptree~=2.13.0` to `pipdeptree~=2.13.1`
- `pyopenssl` dependency upgraded from `pyopenssl~=23.2` to `pyopenssl~=23.3`
- `responses` dependency upgraded from `responses~=0.22.3` to `responses~=0.24`

## [5.1.7] - 2023-10-25

### Changed

- `urllib3` dependency removed, `requests` already solves it.
- `cryptography` depemdency upgraded from `cryptography~=41.0.3` to `cryptography~=41.0.5`
- `msgpack~=1.0.4` testing dependency upgraded from `msgpack~=1.0.4` to `msgpack~=1.0.7`
- `pipdeptree~=2.5.0` testing dependency upgraded from `pipdeptree~=2.5.0` to `pipdeptree~=2.13.0`
- Removed support for Python 3.7.

## [5.1.6] - 2023-10-05

### Changed

- `pyopenssl` dependency upgraded from `pyopenssl~=23.0` to `pyopenssl~=23.2`
- `pytz` dependency upgraded from `pytz~=2019.3` to `pytz~=2023.3`
- `responses` dependency upgraded from `responses~=0.22.0` to `responses~=0.23.3`
- `urllib3` dependency upgraded from `urllib3~=1.26.5` to `urllib3~=2.0.6`
- Log level demoted to warning while closing socket in sender data.

## [5.1.5] - 2023-08-21

### Changed

- `click` dependency upgraded from `click==8.1.3` to `click==8.1.7`
- `pem` dependency open from `pem==21.2.0` to `pem~=21.2.0`
- `pyyaml` dependency open from `pyyaml==6.0.1` to `pyyaml~=6.0.1`
- Code reformatted with `yapf`, `black`, `isort` and `flake8` tools.

### Security

- `certifi` dependency open from `certifi==2021.10.8` to `certifi~=2023.7.22`
- `cryptography` dependency upgraded from `cryptography==41.0.1` to `cryptography~=41.0.3`

## [5.1.4] - 2023-06-13

### Security

- `requests` dependency updated from `requests@2.27` to `requests@2.31`
- `cryptography` dependency updated from `cryptography@39.0.1` to `cryptography@41.0.1`

### Changed

- `pyopenssl` dependency open from `pyopenssl==23.0.*` to `pyopenssl>=23.0`
- Markdown documents reformated.

## [5.1.3] - 2023-03-23

### Fixed

- Fix minor documentation error in `docs/sender/data.md`

## [5.1.2rc2] - 2023-03-21

### Added

- Sender: NonBlocking Socket support added
- `responses` dependency open from ==0.22.0 to >=0.22.0

### Fixed

- Sender: Closing handshake protocol improved to avoid losing of events. Upstream channel is closed and then client waits for the closing of downstream channel
- Sender: Monitoring of the EOF signal in downstream channel to detect whether server endpoint have closed the session
- Fixed message file management in CLI
- Fixed [wrong import](https://github.com/DevoInc/python-sdk/issues/185)

## [5.1.1] - 2023-03-09

### Added

- `msgpack` dependency open from ==1.0.4 to >=1.0.4

## [5.1.0] - 2023-03-07

### Fixed

- Fixed [exception handling issue](https://github.com/DevoInc/python-sdk/issues/175) in `devo/sender/data.py`
- Fixed message shown when configuration file (JSON or YAML) is not correct

### Added

- Client side exception management refactoring for sending and querying data
- Snyk integration for checking dependencies and static code security
- `pipdeptree` dependency open from ==2.5.0 to >=2.5.0

## [5.0.6] - 2023-02-21

### Chore

- Update version range support for `requests`

### Fixed

- Documentation fixes in `README.md` and `docs/common.md`
- Documentation related to testing updated at `README.md`

### Added

- Added `verify-certificates` parameter support in event sending and lookups management clients

## [5.0.5] - 2023-02-20

### Fix

- Fix vulnerability found in dependency `cryptography@38.0.4` inherited from `pyopenssl@22.1.0`

### Added

- Github workflow `Package test` can be triggered manually now
- Dependabot configuration added for security and versions updates

## [5.0.4] - 2023-02-13

### Chore

- Fix documentation (implementation remains the same) for keep-alive mechanism in queries for `xls` format
- Bump version to avoid collision with tag belonging to former release candidate version

## [5.0.3] - 2023-01-26

### Fixed

- Ingestion endpoint has an inactivity timeout that when reached closes the connection. `devo-sdk` is aware of such a timeout and restart connection before is reached. New parameter `inactivity_timeout` in class `Sender` to set up it. Its default value is 30 seconds.
- Syntax error when calling `Path.is_file()`
- Documentation related to parameter `key` removal at `devo.sender.lookup.Lookup.send_data_line` in version 5.0.0

## [5.0.2] - 2023-01-04

### Fixed

- `pyopenssl` dependency bumped

### Changed

- Error messages added to enum

## [5.0.1] - 2022-12-21

### Fixed

- Error when processing some exceptions

## [5.0.0] - 2022-12-02

### Added

- `DevoClientException` and `DevoSenderException` refactored for better details extraction
- In query error detection and feedback through detailed `DevoClientException`
- New test selection in `run_tests.py` tool (included and excluded parameter)

### Removed

- Parameter `key` removed from `devo.sender.lookup.Lookup.send_data_line`. The `key` parameter pointed to the value in the `fields` list that was the key of the lookup item. When the value appeared several times in `fields`, the one expected to be the key cannot be identified. This parameter was set as deprecated since version 3.4.0 (2020-08-06)

### Changed

- API query timeout by default set to 300 seconds, instead of 30
- Retries timeout following Exponential backoff algorithm. Default retry delay base set to 5 seconds
- Retry delay configurable through `retry_delay` instead of `timeout` parameter

## [4.0.3] - 2022-09-12

### Fix

- Added a constraint in client parameters so binary formats like, `msgpack` and `xls`, cannot be invoked without `output`parameter

## [4.0.2] - 2022-09-01

### Added

- Add a new command-line option for escaping double quotes with `-eq` or `--escape_quotes`
- Add a check and shows a warning if the file contains double quotes and the option `-eq` is not used
- Add a new command-line option in tests for testing just one module with `-m <module_name>` or `--module <module_name>`

## [4.0.1] - 2022-08-26

### Added

- Create GitHub action to publish package in PyPI
- Create GitHub action for running tests after a pull request
- Added CSV tests

## [4.0.0] - 2022-08-05

### Changed

- Default retries now are 0. Therefore, no retry mechanism is enabled by default in query API
- Retries parameter is set to default 0 as there are no retries by default. If, after error, one retry is needed, the parameter should be set to 1
- `msgpack` and `xls` response mode know return bytes type in query API

### Fixed

- KeepAlive functionality provided by server now is supported by query API
- Stream modes only supported for `csv`, `tsv`, `json/simple`, `json/simple/compact` modes in query API

## [3.6.4] - 2022-07-21

### Fixed

- Fixed bug when processing keep alive empty tokens

## [3.6.3] - 2022-07-12

### Fixed

- Dependencies updated for `click` and `PyYAML`
- Some small fixes in documentation
- `urllib3` dependencies forced for [CVE-2021-33503](https://nvd.nist.gov/vuln/detail/CVE-2021-33503)
- Query in REST API test to be configurable by environment variable

## [3.6.2] - 2022-05-30

### Fixed

- Some events are not sent completely due to the use of `socket.send()` instead of `socket.sendall()` [#141]

## [3.6.1] - 2022-05-19

### Fixed

- Dependencies added to `setup.py`
- Some documentation fixes, mostly related to dependencies and compatibilities with Python versions

## [3.6.0] - 2022-05-17

### Added

- Sender: certificate files can now be verified with `verify_config=True` or `"verify_config": true` from the config file.
- Internal support for HTTP unsecure API REST endpoint.

### Fixed

- Sender: bad error management when `socker.shutdown` is called and the connection was not established.
- test `test_get_common_names` not running.
- Some environment vars for testing were wrong in the sample file.
- `pem` module added to depedencies

## [3.5.0] - 2022-01-20

### Added

- Double quotes on lookups can be escaped by adding `"escape_quotes": true` to the config file.

### Fixed

- Fix and skip some non-working tests.
- `Lookup.send_headers` method not working as expected with key_index parameter.
- Add `type_of_key` parameter to `Lookup.send_headers` method.
- Avoid lookups' key element to be deleted when `Lookup.send_data_line` is invoked.
- **api-query**: return `None` when the query response has no results.
- Remove `tests` folder from distribution package.

## [3.4.2] - 2021-05-18

### Added

- Update pyyaml version dependency

## [3.4.1] - 2020-11-03

### Added

- Info about use custom CA for verify certificates in client

### Fixed

- Client problems with default "From" key for queries
- Socket closes are more gently now, fixed problems with loss events

### Changed

- Updated message when overwrite sec_level to show only when create Sender
- Updated test for bad credentials. Now api returns error in signature validation

## [3.4.0] - 2020-08-06

### Added

- Support to use in lookup fields lists: ints, booleans and floats. Not necessary send all with str type.
- More documentation in lookup readme

## [3.3.7] - 2020-07-16

### Fixed

- Problem in list_to_headers when pass key but not key_index
- Count of sended events when zip=True
- Problems with key instead of key_index in lookups

## [3.3.6] - 2020-06-30

### Fixed

- Fixed problem with row types in Lookup creation

## [3.3.3] - 2020-06-10

### Fixed

- Fixed (Again) problems with verify flag in Api creation

## [3.3.2] - 2020-06-02

### Fixed

- Fixed problems with Query Eternal queries
- Fixed problems with some flags in Api creation

## [3.3.1] - 2020-05-11

### Added

- env vars JWT and TOKEN for API shell client
- verify certs in API creation and cli calls

### Fixed

- Documentation about SSLConfigSender

### Deprecated

- Unnecesary setters

## [No version upgraded] - 2020-04-29

### Added

- Added examples

### Fixed

- Fixed shebangs
- Fixed typo in README
- Remove one blank in Sender

## [3.3.0] - 2020-04-14

### Added

- Support for Python 3.8
- Testing in Travis for python 3.6, 3.7 and 3.8
- Support in API to timeZone flag for Devo API
- Support in API for new devo custom formats
- Documentation for new date formats
- Functions to change buffer size and compression_level of Sender
- Support for zip, buffer and compression_level flags in Sender CLI

### Changed

- SSL Server support to adapt it from python 3.5 to python 3.8
- SSL Send data tests
- Requirements, updated.

### Removed

- unnecessary elifs in code following PEP8 recomendations

## [3.2.5] - 2020-04-02

### Added

- Added new security flags to Sender SSL Sender

### Changed

- Changed API processors to be able to add custom processors

### Fixed

- Documentation
- Sender CLI missing options

## [3.2.2] - 2020-03-23

### Fixed

- wrongly assigned timeout from configuration

### Added

- "timeout" and "retries" parameters are able to be assigned from environment (DEVO_API_TIMEOUT, DEVO_API_RETRIES)

## [3.2.1] - 2020-03-17

### Changed

- Changed version info in CLI for show only when asked

## [3.2.0] - 2020-01-13

### Added

- Support to Incremental lookups in CLI
- Support to types in lookups
- Auto-detect types for lookups
- Action field for lookups

### Changed

- The documentation of the devo-sender is now separated into data and lookups

### Deprecated

- list_to_fields function in lookups its deprecated and not in use by the internal code. To be deleted in v4 of Devo-sdk

## [3.1.1] - 2019-11-12

### Added

- Support to CA_MD_TOO_WEAK problems with a new flag "sec_level"
- New flag documentation

### Changed

- SSL Socket in Sender creation with custom context
- Tests Sender certificates generation/files are updated

### Fixed

- Problems in documentation with API information

## [3.1.0] - 2019-10-21

### Fixed

- Documentation with examples of version 2.0

### Added

- level flag to handlers in logging and updated documentation
- flag/capacity of Sender to use pfx certificates

### Deprecated

- level for global logging when get_log. We maintain general level until version 4

## [3.0.3] - 2019-09-25

### Fixed

- Fixed reconnection to socket in every send instruction of Sender
- Code style changes
- Added pep8speaks file for Github

## [3.0.2] - 2019-07-01

### Fixed

- API dates when int, verify if len its correct before add 3 zero
- Problem overriding tag when use Sender for logging

## [3.0.1] - 2019-06-27

### Fixed

- Fixed always debug on reconnection

## [3.0.0] - 2019-04-26

### Removed

- Support to Python 2.7
- Configuration class "key_exist()" and "keys()" functions
- Api and Sender "from_config" are now removed and included in Class init flag

### Added

- for_logging option in Sender, added more values
- Logging streamhandler
- Tests for CLI
- Have Client query method accept Unix timestamps for to and from dates
- Make Client parameters retries, timeout, and sleep configurable
- CLI of devo-sdk now has --version flag.

### Changed

- Errors exceptions in API and Sender are now full controlled and homogenized
- logging in Common now are created more flexible
- Sender init class, SSLSender and TCPSender too.
- API init class
- New documentation
- Now devo Configuration object inherits from the dict class
- Configuration set and get are now more dict homogenized
- vars/flags "url" are now like python: "address" and are now tuples
- New "auth" flag to encapsulate key, secret, jwt and token
- Env var "DEVO_AUTH_TOKEN" to "DEVO_API_TOKEN"
- Env var "DEVO_API_URL" to "DEVO_API_ADDRESS"

### Fixed

- Fixed when add key chain to configuration
- Fixed problems with API CLI Config objects
- Fixed problems with SENDER CLI Config objects
- API Proccessors
- Problems with multiline and zip when both are activated

## [2.2.4] - 2019-04-25

### Fixed

- Fixed multiline sending introduced in version 1.3.0

## [2.2.3] - 2019-04-22

### Fixed

- Fixed bug in Sender CLI introduced in version 2.2.2

## [2.2.2] - 2019-04-03

### Fixed

- Sender for logging (Handler) get Severity correctly when use custom Level info

## [2.2.1] - 2019-03-28

### Fixed

- Lookup shell client now read config correctly
- Lookup shell client now apply default port if empty

### Changed

- API response in stream mode now return response object if response.code its not 200

## [2.2.0] - 2019-02-23

### Changed

- Inits args for Sender(), and from_config(), to make it more flexible to config objects and flags

## [2.1.3] - 2019-02-22

### Added

- Requirements file
- .pyup.yaml file for security dependencies bot

### Fixed

- Logging when send data in multiline or zipped
- Error of for_logging() function in Sender when applicate level

## [2.1.2] - 2019-02-12

### Added

- More documentation info and examples

### Changed

- All new endpoints references for sender and api

### Fixed

- Problems with proc_json_compact_simple_to_jobj when None

## [2.1.1] - 2019-01-29

### Fixed

- Problems with recursion depth when zipped send has problems with Socket.

## [2.1.0] - 2019-01-28

### Changed

- Devo.common get_log() has more flags for better customization

### Added

- Sender for_logging() creation now verify where is tag flag
- Functions for configuration (save, len, etc)
- Added verify flag for API, for not verify TLS certs

## [2.0.2] - 2019-01-23

### Fixed

- devo.common logging handler
- Errors response in devo.api

## [2.0.0] - 2019-01-21

### Changed

- Changed all logic in API calls for stream and non stream calls, improving speed in streaming x3
- API responses are now iterator
- Rollback to request sockets instead of custom sockets in API
- Rollback to one class in Client, instead of Base and Client
- Behavior of the processors, optimizing their performance and only allowing default processors/flags, within the API

### Removed

- Buffer files
- chain_dict files

### Deprecated

- Buffer item
- Old custom processors functions in API calls

## [1.6.3] - 2019-01-17

### Fixed

- Broken urls in documentations

### Changed

- Inconsistences in api.base class
- PEP8/Pylint styles in api and common packages

## [1.6.2] - 2019-01-16

### Added

- Documentation about API "destination" parameter
- Task management with API Client: added functions, documentation

### Changed

- Travis CI configuration
- Refactoring of API, separated now in two files
- Reorganized API documentation

## [1.6.1] - 2019-01-10

### Changed

- Refactoring of devo.common.dates from objects to simple functions
- Now API return bytes in Python 3 and str in Python 2 by default

### Fixed

- Problems with non ascii/utf-8 characters in API
- Travis CI autodeploy to pypi

### Added

- Travis CI upload wheel to release on github

## [1.6.0] - 2019-01-09

### Changed

- Mild refactoring of Sender class
- Refactoring API Response processing
- Typos in docs
- API Socket recv size

### Fixed

- API responses blank lines and splitted lines
- Problems with API CLI and automatic shutdowns

## [1.5.1] - 2018-12-28

### Fixed

- devo.common buffer now receive data when CSV response
- devo.common buffer.is_empty

### Added

- Travis CI deploy automatic options

## [1.5.0] - 2018-12-27

### Changed

- Modify Configuration loads functions
- Now Sender send, send_raw, flush_buffer and fill_buffer return the number of lines sent

### Fixed

- Problems when loads configuration from default sites
- Problems with local_server

## [1.4.0] - 2018-12-17

### Added

- Allow the parameters user, application name and comment to queries
- Add tests (test_pragmas and test_pragmas test_pragmas_not_comment_free) in the query.py file.

### Fixed

- Problems when API CAll query has not "to", now added be default "now()" if not to in no stream mode

## [1.3.1] - 2018-12-04

### Fixed

- Somes revert changes in pull request error are back again

## [1.3.0] - 2018-12-03

### Added

- Use of Token auth and JWT in API, added docs and tests
- Local servers for tests
- YAML file for Travis CI tests

### Fixed

- ConnectionError in python 2
- tests of Sender  
- Close order of API/Buffer

### Changed

- Modify Client init class
- License file

### Removed

- Dockerfile

## [1.2.1] - 2018-11-26

### Added

- YAML configuration files, like JSON files.
- YAML configuration file information in all docs.
- EXTRA_REQUIRES option for YAML support
- Default Yaml file load in Common

### Changed

- Removed the octec count for performance, and verify if "\n" at the end of each msg, if applicable.
- Modify classes to privates
- Public functions to private in API
- Update documentation of Sender and API

### Removed

- Unused class "Props" on Sender, included in past versions
- Bad class debug for Sender, unused too
- Memoize class from Common namespase
- Memoize references in Common readme.

## [1.2.0] - 2018-11-16

### Added

- Int conversion for SenderSSL and SenderTCP classes in port value
- is_empty, set_timeout and close functions for Buffer class

### Changed

- Modified how API flow work
- Modified Buffer class to avoid failures by timeouts and emptys that block the threads
- Updated documentation

## [1.1.4] - 2018-11-15

### Changed

- Modified Sender init class for kwargs arguments

## [1.1.3] - 2018-11-08

### Added

- Sender class inherits from logging.handlers

## [1.1.2] - 2018-10-26

### Added

- Long description value in setup for pypi

### Fixed

- Fixed problems when zip msgs dont have "\n" in each line msg

## [1.1.1] - 2018-10-19

### Added

- Added flush buffer in send data when socket is closed

### Changed

- Modified documentation for new cert_reqs flag changed

## [1.1.0] - 2018-10-19

### Changed

- Tests and requirements for Sender

### Fixed

- Problems with double "\n" in messages
- Sender CLI problems when no certs required

## [1.0.4] - 2018-10-03

### Added

- More error prevention in API
- More debug information when exceptions occur in API

### Changed

- Strings joins for test files in Sender and Lookup tests
- Name of internal vars in sender tests
- API docs examples

### Fixed

- API urls in docs, examples and code

## [1.0.3] - 2018-10-01

### Added

- Documentation of .devo.json file
- Contributors lists
- test function for setup.py

### Changed

- API response when code are not 404 or 200 give more info now

### Fixed

- Fixed API EU default url in code and documentation

## [1.0.2] - 2018-09-24

### Added

- Dockerfile now rm some folders for to avoid problems when there are several builds
- More Sender examples in docs/sender.md
- More info about config.json file in sender, api and common doc
- config.example.json in docs/common for give more info about config files for easy use

### Changed

- Sender.from_config con_type default is None, and change how to manage default var into the function
- Changed how to manage certs_req value into function Sender.from_config

### Fixed

- Sender.from_config now use the correct param "certs_req", not wrong/old "certreq"

## [1.0.1] - 2018-09-14

### Added

- Docker file for testing purposes
- Example vars in environment.env example file

### Changed

- Updated option of not launch TCP tests for no-devo developers
- .gitignore file

### Fixed

- Zip flag in Devo Sender
- Problems with QueryId and normal query in payload

## [1.0.0] - 2018-09-05

### Added

- On the ninth month of the year, a Devo programmer finally decided to publish a part of the SDK and rest in peace.
