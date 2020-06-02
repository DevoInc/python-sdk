# -*- coding: utf-8 -*-

"""
This file parse dates and provide some helpers for the very basic usage
"""

from datetime import datetime as dt

import sys
from .dateutils import test_date_format, to_millis, trunc_time
from .dateoperations import parse_functions


def parse(date_string=None, default='now'):
    """
    Parse a date string and return the result
    :param date_string: Date in string format
    :param default: Default date for use in case date_string is None
    :return: Millis from parse date
    """
    if date_string is None:
        return parse_string(default)
    return parse_string(date_string)


def parse_string(date_string):
    """
    Parse string to millis by a fixed format or an expression
    :param date_string: String to parse
    :return: Millis
    """
    if test_date_format(date_string, '%Y-%m-%d %H:%M:%S'):
        date = dt.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return to_millis(date)
    if test_date_format(date_string, '%Y-%m-%d'):
        date = dt.strptime(date_string, '%Y-%m-%d')
        return to_millis(trunc_time(date))
    return parse_expression(date_string)


def parse_expression(date_string):
    """
    Evaluate a date string expression for use controlled functions
    :param date_string: Date string
    :return: The millis evaluated from the expression
    """
    ops = parse_functions()
    try:
        try:
            result = eval(date_string, None, ops)
        except Exception:
            return date_string
        if isinstance(result, type(lambda x: 0)):
            return date_string
        return result
    except SyntaxError as err:
        sys.exit('ERROR: Syntax error on parse dates: ' + str(err))
    except TypeError as err:
        sys.exit('ERROR: Type error on parse dates: ' + str(err))
    except Exception as err:
        sys.exit('ERROR: Unknown error on parse dates: ' + str(err))


def default_from(date=None):
    """
    Helper for return date with the default as ()
    :param date: Date in the accepted formats
    :return: Millis for the API
    """
    if isinstance(date, int):
        if len(str(abs(date))) == 10:
            return date * 1000
        return date
    return parse(date, 'now()-day()')


def default_to(date=None):
    """
    Helper for return date with the default as now()
    :param date: Date in the accepted formats
    :return: Millis for the API
    """

    if isinstance(date, int):
        if len(str(abs(date))) == 10:
            return date * 1000
        return date
    return parse(date, 'now()')
