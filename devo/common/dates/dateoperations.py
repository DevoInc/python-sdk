# -*- coding: utf-8 -*-
"""A collection of allowed operations on date parsing"""
from datetime import datetime as dt, timedelta
from .dateutils import to_millis, trunc_time, trunc_time_minute


def month():
    """
    Return millis for a month
    :return: 30 * 24 * 60 * 60 * 1000
    """
    return 2592000000


def week():
    """
    Return millis for a week
    :return: 7 * 24 * 60 * 60 * 1000
    """
    return 604800000


def day():
    """
    Return millis for a day
    :return: 24 * 60 * 60 * 1000
    """
    return 86400000


def hour():
    """
    Return millis for an hour
    :return: Return 60 * 60 * 1000
    """
    return 3600000


def minute():
    """
    Return millis for a minute
    :return: 60 * 1000
    """
    return 60000


def second():
    """
    Return millis for a second
    :return: 1000
    """
    return 1000


def now():
    """
    Return current millis in UTC
    :return: Millis
    """
    return to_millis(dt.utcnow())


def now_without_ms():
    """
    Return current millis in UTC
    :return: Millis
    """
    return to_millis(trunc_time_minute(dt.utcnow()))


def today():
    """
    Return current millis with the time truncated to 00:00:00
    :return: Millis
    """
    return to_millis(trunc_time(dt.utcnow()))


def yesterday():
    """
    Return millis from yesterday with time truncated to 00:00:00
    :return: Millis
    """
    return to_millis(trunc_time(dt.utcnow()) - timedelta(days=1))


def parse_functions():
    """Return object with all functions availables"""
    return {
        "month": month,
        "week": week,
        "day": day,
        "hour": hour,
        "minute": minute,
        "second": second,
        "now": now,
        "now_without_ms": now_without_ms,
        "today": today,
        "yesterday": yesterday
    }
