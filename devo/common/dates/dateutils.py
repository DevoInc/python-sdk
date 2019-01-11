# -*- coding: utf-8 -*-
"""Utils for format and trunc dates."""

from datetime import datetime as dt


def to_millis(date):
    """
    Parse a date to millis
    :param date: Date for parse to millis
    :return: Millis from the date
    """
    return int((date - dt.utcfromtimestamp(0)).total_seconds() * 1000)


def trunc_time(date):
    """
    Truncate an object of type DateTime with time to 00:00:00
    :param date: Date for truncate
    :return: Date truncated
    """
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def trunc_time_minute(date):
    """
    Truncate an object of type DateTime with time to 00:00:00
    :param date: Date for truncate
    :return: Date truncated
    """
    return date.replace(second=0, microsecond=0)


def test_date_format(date, date_format):
    """
    Test date format on string
    :param date: The date string to check
    :param date_format: The format as python datetime format
    :return: True if the string is in that format, False in other ways
    """
    try:
        dt.strptime(date, date_format)
        return True
    except ValueError:
        return False


def get_timestamp():
    """
    Generate current timestamp
    :return:
    """
    return to_millis(dt.utcnow())
