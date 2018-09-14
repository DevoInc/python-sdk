# -*- coding: utf-8 -*-
"""Utils for date parsers."""

from datetime import datetime as dt
import sys

from .dateutils import DateUtils
from .dateoperations import DateOperations


class DateParser(object):
    """
    This class parse dates and provide some helpers for the very basic usage
    """

    @staticmethod
    def parse(date_string=None, default='now()'):
        """
        Parse a date string and return the result
        :param date_string: Date in string format
        :param default: Default date for use in case date_string is None
        :return: Millis from parse date
        """
        if date_string is None:
            return DateParser.parse_string(default)
        return DateParser.parse_string(date_string)

    @staticmethod
    def parse_string(date_string):
        """
        Parse string to millis by a fixed format or an expression
        :param date_string: String to parse
        :return: Millis
        """
        if DateUtils.test_date_format(date_string, '%Y-%m-%d %H:%M:%S'):
            date = dt.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            return DateUtils.to_millis(date)
        elif DateUtils.test_date_format(date_string, '%Y-%m-%d'):
            date = dt.strptime(date_string, '%Y-%m-%d')
            return DateUtils.to_millis(DateUtils.trunc_time(date))
        return DateParser.parse_expression(date_string)

    @staticmethod
    def parse_expression(date_string):
        """
        Evaluate a date string expression for use controlled functions
        :param date_string: Date string
        :return: The millis evaluated from the expression
        """
        ops_obj = DateOperations()
        ops = {k: getattr(ops_obj, k) for k in dir(ops_obj)}
        try:
            return eval(date_string, None, ops)
        except SyntaxError as err:
            sys.exit('ERROR: Syntax error on parse dates: ' + str(err))
        except TypeError as err:
            sys.exit('ERROR: Type error on parse dates: ' + str(err))
        except Exception as err:
            sys.exit('ERROR: Unknown error on parse dates: ' + str(err))

    @staticmethod
    def default_from(date=None):
        """
        Helper for return date with the default as ()
        :param date: Date in the accepted formats
        :return: Millis for the API
        """
        return DateParser.parse(date, 'now()-day()')

    @staticmethod
    def default_to(date=None):
        """
        Helper for return date with the default as now()
        :param date: Date in the accepted formats
        :return: Millis for the API
        """
        return DateParser.parse(date, 'now()')
