# Devo Common library
## Overview
This library add utilities for other packages.

## Features

- Unification in the way of treating date formats
- Unification in the way of treating configuration files
- Logging functions
- Custom memoize def

#### Date Formats
- Fixed format: As described on [Official Python Docs](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior). Accepted formats are:
    - '%Y-%m-%d %H:%M:%S'
    - '%Y-%m-%d', the time will be truncated to 00:00:00
- Timestamp: From epoch in millis
- Dynamic expression: Using the LinQ sintax we can use several functions
    - Relative functions:
        - now(): Current date and time
        - today(): Current date and time fixed to 00:00:00
        - yesterday(): Current date minus one day and time fixed to 00:00:00
    - Amount functions:
        - second(): Return 1
        - minute(): Return 60
        - hour(): Return 60 * 60
        - day(): Return 24 * 60 * 60
        - week(): Return 7 * 24 * 60 * 60
        - month(): Return 30 * 24 * 60 * 60


#### Standard Devo configuration file

Devo Common contains the [`Configuration`](common/generic/configuration.py) 
class to read JSON configuration files 
and automix an array with the file.

You can see in several Devo libraries that the CLI allows the reading of a 
config.json file, they all use this class to load them, and in each of the 
libraries you can find the format they use, in addition to examples of use in 
this class tests.

#### Memoize
Decorator. Caches a function's return value each time it is called.
If called later with the same arguments, the cached value is returned 
(not reevaluated)
