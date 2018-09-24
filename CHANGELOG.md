# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


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