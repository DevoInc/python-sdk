# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [Unreleased] - xxxx-xx-xx
#### Added
 * YAML configuration files, like JSON files.
 * YAML configuration file information in all docs.
 * EXTRA_REQUIRES option for YAML support
 * Default Yaml file load in Common
 
#### Changed
 * Removed the octec count for performance, and verify if "\n" at the end of each msg, if applicable.
 * Modify classes to privates.
 * Public functions to private in API.
 * Update documentation of Sender and API.
 
### Fixed
 * Return of "info" function in Sender class, this fix use and tests

#### Removed
 * Unused class "Props" on Sender, included in past versions.
 * Bad class info and debug for Sender, unused too.
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