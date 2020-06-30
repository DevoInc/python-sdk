# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [3.3.4] - 2020-06-30
### Fixed
 * Fixed problem with row types in Lookup creation
 
## [3.3.3] - 2020-06-10
### Fixed
 * Fixed (Again) problems with verify flag in Api creation

## [3.3.2] - 2020-06-02
### Fixed
 * Fixed problems with Query Eternal queries
 * Fixed problems with some flags in Api creation

## [3.3.1] - 2020-05-11
### Added
 * env vars JWT and TOKEN for API shell client
 * verify certs in API creation and cli calls
 
### Fixed
 * Documentation about SSLConfigSender
 
### Deprecated
 * Unnecesary setters

## [No version upgraded] - 2020-04-29
### Added
 * Added examples
 
### Fixed
 * Fixed shebangs
 * Fixed typo in README
 * Remove one blank in Sender

## [3.3.0] - 2020-04-14
### Added
 * Support for Python 3.8
 * Testing in Travis for python 3.6, 3.7 and 3.8
 * Support in API to timeZone flag for Devo API
 * Support in API for new devo custom formats
 * Documentation for new date formats
 * Functions to change buffer size and compression_level of Sender
 * Support for zip, buffer and compression_level flags in Sender CLI

 
### Changed
 * SSL Server support to adapt it from python 3.5 to python 3.8
 * SSL Send data tests 
 * Requirements, updated.
 
#### Removed
 * unnecessary elifs in code following PEP8 recomendations
 
## [3.2.5] - 2020-04-02
### Added
 * Added new security flags to Sender SSL Sender
 
### Changed
 * Changed API processors to be able to add custom processors
 
#### Fixed
 * Documentation
 * Sender CLI missing options
 
## [3.2.2] - 2020-03-23
#### Fixed
 * wrongly assigned timeout from configuration

#### Added
 * "timeout" and "retries" parameters are able to be assigned from environment (DEVO_API_TIMEOUT, DEVO_API_RETRIES)

## [3.2.1] - 2020-03-17
### Changed
 * Changed version info in CLI for show only when asked

## [3.2.0] - 2020-01-13
#### Added
 * Support to Incremental lookups in CLI
 * Support to types in lookups
 * Auto-detect types for lookups
 * Action field for lookups

#### Changed
 * The documentation of the devo-sender is now separated into data and lookups

#### Deprecated
 * list_to_fields function in lookups its deprecated and not in use by the internal code. To be deleted in v4 of Devo-sdk

## [3.1.1] - 2019-11-12
#### Added
 * Support to CA_MD_TOO_WEAK problems with a new flag "sec_level"
 * New flag documentation
 
#### Changed
 * SSL Socket in Sender creation with custom context
 * Tests Sender certificates generation/files are updated
 
#### Fixed
 * Problems in documentation with API information

## [3.1.0] - 2019-10-21
#### Fixed
 * Documentation with examples of version 2.0
 
#### Added
 * level flag to handlers in logging and updated documentation
 * flag/capacity of Sender to use pfx certificates
#### Deprecated
 * level for global logging when get_log. We maintain general level until version 4

## [3.0.3] - 2019-09-25
#### Fixed
 * Fixed reconnection to socket in every send instruction of Sender
 * Code style changes
 * Added pep8speaks file for Github


## [3.0.2] - 2019-07-01
#### Fixed
 * API dates when int, verify if len its correct before add 3 zero
 * Problem overriding tag when use Sender for logging

## [3.0.1] - 2019-06-27
#### Fixed
 * Fixed always debug on reconnection

## [3.0.0] - 2019-04-26
#### Removed
 * Support to Python 2.7
 * Configuration class "key_exist()" and "keys()" functions
 * Api and Sender "from_config" are now removed and included in Class init flag

#### Added
 * for_logging option in Sender, added more values
 * Logging streamhandler
 * Tests for CLI
 * Have Client query method accept Unix timestamps for to and from dates
 * Make Client parameters retries, timeout, and sleep configurable
 * CLI of devo-sdk now has --version flag.

#### Changed
 * Errors exceptions in API and Sender are now full controlled and homogenized
 * logging in Common now are created more flexible
 * Sender init class, SSLSender and TCPSender too.
 * API init class
 * New documentation
 * Now devo Configuration object inherits from the dict class
 * Configuration set and get are now more dict homogenized
 * vars/flags "url" are now like python: "address" and are now tuples
 * New "auth" flag to encapsulate key, secret, jwt and token
 * Env var "DEVO_AUTH_TOKEN" to "DEVO_API_TOKEN"
 * Env var "DEVO_API_URL" to "DEVO_API_ADDRESS"
 
#### Fixed
 * Fixed when add key chain to configuration
 * Fixed problems with API CLI Config objects
 * Fixed problems with SENDER CLI Config objects
 * API Proccessors
 * Problems with multiline and zip when both are activated

## [2.2.4] - 2019-04-25
#### Fixed
 * Fixed multiline sending introduced in version 1.3.0

## [2.2.3] - 2019-04-22
#### Fixed
 * Fixed bug in Sender CLI introduced in version 2.2.2

## [2.2.2] - 2019-04-03
#### Fixed
 * Sender for logging (Handler) get Severity correctly when use custom Level info

## [2.2.1] - 2019-03-28
#### Fixed
 * Lookup shell client now read config correctly
 * Lookup shell client now apply default port if empty

#### Changed
 * API response in stream mode now return response object if response.code its not 200

## [2.2.0] - 2019-02-23
#### Changed
 * Inits args for Sender(), and from_config(), to make it more flexible to config objects and flags

## [2.1.3] - 2019-02-22
#### Added
 * Requirements file
 * .pyup.yaml file for security dependencies bot

#### Fixed
 * Logging when send data in multiline or zipped
 * Error of for_logging() function in Sender when applicate level

## [2.1.2] - 2019-02-12
#### Added
 * More documentation info and examples

#### Changed
 * All new endpoints references for sender and api

#### Fixed
 * Problems with proc_json_compact_simple_to_jobj when None

## [2.1.1] - 2019-01-29
#### Fixed
 * Problems with recursion depth when zipped send has problems with Socket.

## [2.1.0] - 2019-01-28
#### Changed
 * Devo.common get_log() has more flags for better customization

#### Added
 * Sender for_logging() creation now verify where is tag flag
 * Functions for configuration (save, len, etc)
 * Added verify flag for API, for not verify TLS certs

## [2.0.2] - 2019-01-23
#### Fixed
 * devo.common logging handler
 * Errors response in devo.api

## [2.0.0] - 2019-01-21
#### Changed
 * Changed all logic in API calls for stream and non stream calls, improving speed in streaming x3
 * API responses are now iterator
 * Rollback to request sockets instead of custom sockets in API
 * Rollback to one class in Client, instead of Base and Client
 * Behavior of the processors, optimizing their performance and only allowing default processors/flags, within the API

#### Removed
 * Buffer files
 * chain_dict files

#### Deprecated
 * Buffer item
 * Old custom processors functions in API calls


## [1.6.3] - 2019-01-17
#### Fixed
 * Broken urls in documentations

#### Changed
 * Inconsistences in api.base class
 * PEP8/Pylint styles in api and common packages

## [1.6.2] - 2019-01-16
#### Added
 * Documentation about API "destination" parameter
 * Task management with API Client: added functions, documentation

#### Changed
 * Travis CI configuration
 * Refactoring of API, separated now in two files
 * Reorganized API documentation

## [1.6.1] - 2019-01-10
#### Changed
 * Refactoring of devo.common.dates from objects to simple functions
 * Now API return bytes in Python 3 and str in Python 2 by default

#### Fixed
 * Problems with non ascii/utf-8 characters in API
 * Travis CI autodeploy to pypi

#### Added
 * Travis CI upload wheel to release on github

## [1.6.0] - 2019-01-09
#### Changed
 * Mild refactoring of Sender class
 * Refactoring API Response processing
 * Typos in docs
 * API Socket recv size

#### Fixed
 * API responses blank lines and splitted lines
 * Problems with API CLI and automatic shutdowns

## [1.5.1] - 2018-12-28
#### Fixed
 * devo.common buffer now receive data when CSV response
 * devo.common buffer.is_empty

#### Added
 * Travis CI deploy automatic options

## [1.5.0] - 2018-12-27
#### Changed
 * Modify Configuration loads functions
 * Now Sender send, send_raw, flush_buffer and fill_buffer return the number of lines sent

#### Fixed
 * Problems when loads configuration from default sites
 * Problems with local_server

## [1.4.0] - 2018-12-17
#### Added
 * Allow the parameters user, application name and comment to queries
 * Add tests (test_pragmas and test_pragmas test_pragmas_not_comment_free) in the query.py file.

#### Fixed
 * Problems when API CAll query has not "to", now added be default "now()" if not to in no stream mode

## [1.3.1] - 2018-12-04
#### Fixed
 * Somes revert changes in pull request error are back again

## [1.3.0] - 2018-12-03
#### Added
 * Use of Token auth and JWT in API, added docs and tests
 * Local servers for tests
 * YAML file for Travis CI tests

#### Fixed
 * ConnectionError in python 2
 * tests of Sender  
 * Close order of API/Buffer

#### Changed
 * Modify Client init class
 * License file

#### Removed
 * Dockerfile

## [1.2.1] - 2018-11-26
#### Added
 * YAML configuration files, like JSON files.
 * YAML configuration file information in all docs.
 * EXTRA_REQUIRES option for YAML support
 * Default Yaml file load in Common

#### Changed
 * Removed the octec count for performance, and verify if "\n" at the end of each msg, if applicable.
 * Modify classes to privates
 * Public functions to private in API
 * Update documentation of Sender and API

#### Removed
 * Unused class "Props" on Sender, included in past versions
 * Bad class debug for Sender, unused too
 * Memoize class from Common namespase
 * Memoize references in Common readme.

## [1.2.0] - 2018-11-16
#### Added
 * Int conversion for SenderSSL and SenderTCP classes in port value
 * is_empty, set_timeout and close functions for Buffer class

#### Changed
 * Modified how API flow work
 * Modified Buffer class to avoid failures by timeouts and emptys that block the threads
 * Updated documentation

## [1.1.4] - 2018-11-15
#### Changed
 * Modified Sender init class for kwargs arguments

## [1.1.3] - 2018-11-08
#### Added
 * Sender class inherits from logging.handlers

## [1.1.2] - 2018-10-26
#### Added
 * Long description value in setup for pypi

#### Fixed
 * Fixed problems when zip msgs dont have "\n" in each line msg

## [1.1.1] - 2018-10-19
#### Added
 * Added flush buffer in send data when socket is closed

#### Changed
 * Modified documentation for new cert_reqs flag changed

## [1.1.0] - 2018-10-19
#### Changed
 * Tests and requirements for Sender

#### Fixed
 * Problems with double "\n" in messages
 * Sender CLI problems when no certs required

## [1.0.4] - 2018-10-03
#### Added
 * More error prevention in API
 * More debug information when exceptions occur in API

#### Changed
 * Strings joins for test files in Sender and Lookup tests
 * Name of internal vars in sender tests
 * API docs examples

#### Fixed
 * API urls in docs, examples and code

## [1.0.3] - 2018-10-01
#### Added
 * Documentation of .devo.json file
 * Contributors lists
 * test function for setup.py

#### Changed
 * API response when code are not 404 or 200 give more info now

#### Fixed
 * Fixed API EU default url in code and documentation


## [1.0.2] - 2018-09-24
#### Added
 * Dockerfile now rm some folders for to avoid problems when there are several builds
 * More Sender examples in docs/sender.md
 * More info about config.json file in sender, api and common doc
 * config.example.json in docs/common for give more info about config files for easy use

#### Changed
 * Sender.from_config con_type default is None, and change how to manage default var into the function
 * Changed how to manage certs_req value into function Sender.from_config

#### Fixed
 * Sender.from_config now use the correct param "certs_req", not wrong/old "certreq"

## [1.0.1] - 2018-09-14
#### Added
 * Docker file for testing purposes
 * Example vars in environment.env example file

#### Changed
 * Updated option of not launch TCP tests for no-devo developers
 * .gitignore file

#### Fixed
 * Zip flag in Devo Sender
 * Problems with QueryId and normal query in payload

## [1.0.0] - 2018-09-05
#### Added
 * On the ninth month of the year, a Devo programmer finally decided to publish a part of the SDK and rest in peace.
