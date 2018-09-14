# -*- coding: utf-8 -*-
"""Utils for date operations."""
from datetime import datetime as dt, timedelta
from .dateutils import DateUtils


class DateOperations(object):
    """
    This class is a collection of allowed operations on date parsing
    """

    @staticmethod
    def month():
        """
        Return millis for a month
        :return: 30 * 24 * 60 * 60 * 1000
        """
        return 2592000000

    @staticmethod
    def week():
        """
        Return millis for a week
        :return: 7 * 24 * 60 * 60 * 1000
        """
        return 604800000

    @staticmethod
    def day():
        """
        Return millis for a day
        :return: 24 * 60 * 60 * 1000
        """
        return 86400000

    @staticmethod
    def hour():
        """
        Return millis for an hour
        :return: Return 60 * 60 * 1000
        """
        return 3600000

    @staticmethod
    def minute():
        """
        Return millis for a minute
        :return: 60 * 1000
        """
        return 60000

    @staticmethod
    def second():
        """
        Return millis for a second
        :return: 1000
        """
        return 1000

    @staticmethod
    def now():
        """
        Return current millis in UTC
        :return: Millis
        """
        return DateUtils.to_millis(dt.utcnow())

    @staticmethod
    def now_without_ms():
        """
        Return current millis in UTC
        :return: Millis
        """
        return DateUtils.to_millis(DateUtils.trunc_time_minute(dt.utcnow()))

    @staticmethod
    def today():
        """
        Return current millis with the time truncated to 00:00:00
        :return: Millis
        """
        return DateUtils.to_millis(DateUtils.trunc_time(dt.utcnow()))

    @staticmethod
    def yesterday():
        """
        Return millis from yesterday with time truncated to 00:00:00
        :return: Millis
        """
        date = DateUtils.trunc_time(dt.utcnow()) - timedelta(days=1)
        return DateUtils.to_millis(date)
