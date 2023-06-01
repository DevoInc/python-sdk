# Devo Common library

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Devo Common library](#devo-common-library)
  - [Overview](#overview)
  - [Features](#features)
    - [Date formats considerations](#date-formats-considerations)
    - [Standard Devo logging file](#standard-devo-logging-file)
      - [StreamHandler](#streamhandler)
      - [RotatingFileHandler](#rotatingfilehandler)
      - [DevoHandler](#devohandler)
  - [Standard Devo configuration file](#standard-devo-configuration-file)

<!-- /code_chunk_output -->

## Overview

This library add utilities for other packages.

## Features

- Unification in the way of treating date formats
- Unification in the way of treating configuration files
- Logging functions

### Date formats considerations

- Fixed format: As described on [Official Python Docs](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior). Accepted formats are:
  - '%Y-%m-%d %H:%M:%S'
  - '%Y-%m-%d', the time will be truncated to 00:00:00
- Timestamp: From epoch (keep in mind API interface uses epoch in **seconds**)
- Dynamic expression: Using the LinQ sintax we can use several functions
  - Relative functions:
    - now(): Current date and time
    - today(): Current date and time fixed to 00:00:00
    - yesterday(): Current date minus one day and time fixed to 00:00:00
  - Amount functions:
    - second(): Return 1
    - minute(): Return 60
    - hour(): Return 60 * 60
    - day(): Return 24 *60* 60
    - week(): Return 7 *24* 60 * 60
    - month(): Return 30 *24* 60 * 60

### Standard Devo logging file

Devo commons gives you a function, with enough parameters for your personalization, to get a logging object:

```python
def get_log(name="log", level=None, handler=None)
```

By default, handler will be a RotatingFileHandler, named history.log, 5 files, in work folder.
You can use other Handler, by you own or using one of the common package.

If you set level, all handlers has the same level, if you want different levels, pass level to handlers,
and not to logger.

#### StreamHandler

```python
def get_stream_handler(dest=sys.stdout,
                       msg_format='%(asctime)s|%(levelname)s|%(message)s',
                       level=logging.DEBUG)
```

With this function you will obtain a StreamHandler, by default the whole log will be to stdout.

```python
from devo.common import get_log, get_stream_handler
my_logger = get_log(handler=get_stream_handler())
```

#### RotatingFileHandler

The default handler for logging, return a handler, you can modify the default parameters in constructor:

```python
def get_rotating_file_handler(path="./",
                              file_name="history.log",
                              msg_format='%(asctime)s|%(levelname)s|%(message)s',
                              max_size=2097152,
                              backup_count=5, 
                              level=logging.DEBUG):
```

You can use this handler like in the StreamHandler example

#### DevoHandler

You can use this Devo Sender like handler, you can see more info in ['Sender readme'](sender/sender.md)

## Standard Devo configuration file

Devo Common contains the [`Configuration`](common/generic/configuration.py)
class to read JSON and YAML configuration files
and automix an array with the file.

It is basically a class that inherits from "dict", so it has all its
functionalities and those that we add

You can see in several Devo libraries that the CLI allows the reading of a
config.json file, they all use this class to load them, and in each of the
libraries you can find the format they use, in addition to examples of use in
this class tests.

You can read json or yaml file and save to obj faster:

```python
from devo.common import Configuration

config = Configuration("/path/o/my/file.yaml")
```

You can use all these options for access, modify or use this  object:

```python
from devo.common import Configuration

#Create
config = Configuration("/path/o/my/file.yaml")


# Get key
value = config['keyOne']
# or
value = config.get("keyOne")
# ---

# Get key chain
value = config['keyOne']['subKey']['id']
# or
value = config.get(["keyOne", "subKey", "id"])
# ---


# Set key
config['keyTwo'] = "value"
# or
config.set('keyTwo', "value")
# ---

# Set key chain
config['keyTwo'] = {}
config['keyTwo']['subKey'] = {}
config['keyTwo']['subKey']['id'] = "value"

# or
config['keyTwo'] = {'subkey': {'id': "value"}}

# or
config.set(["keyTwo", "subKey", "id"], "value")


# Save to file
config.save("file/path.ext")
```
