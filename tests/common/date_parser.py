import unittest
from datetime import datetime as dt

from devo.common import default_from, default_to


class TestDateParser(unittest.TestCase):
    epoch = dt.utcfromtimestamp(0)

    # Tests defaults
    # --------------------------------------------------------------------------

    def test_default_to(self):
        ts1 = default_to()
        ts2 = int((dt.utcnow() - self.epoch).total_seconds() * 1000)
        self.assertTrue(ts1 == ts2)

    def test_default_from(self):
        ts1 = default_from()
        ts2 = int((dt.utcnow() - self.epoch).total_seconds() * 1000) - 86400000
        self.assertTrue(ts1 == ts2)

    # Tests amounts
    # --------------------------------------------------------------------------

    def test_second(self):
        ts1 = default_from('second()')
        ts2 = 1000
        self.assertTrue(ts1 == ts2)

    def test_minute(self):
        ts1 = default_from('minute()')
        ts2 = 60 * 1000
        self.assertTrue(ts1 == ts2)

    def test_hour(self):
        ts1 = default_from('hour()')
        ts2 = 60 * 60 * 1000
        self.assertTrue(ts1 == ts2)

    def test_day(self):
        ts1 = default_from('day()')
        ts2 = 24 * 60 * 60 * 1000
        self.assertTrue(ts1 == ts2)

    def test_week(self):
        ts1 = default_from('week()')
        ts2 = 7 * 24 * 60 * 60 * 1000
        self.assertTrue(ts1 == ts2)

    def test_month(self):
        ts1 = default_from('month()')
        ts2 = 30 * 24 * 60 * 60 * 1000
        self.assertTrue(ts1 == ts2)

    # Tests relatives
    # --------------------------------------------------------------------------

    def test_now(self):
        ts1 = default_from('now()')
        ts2 = int((dt.utcnow() - self.epoch).total_seconds() * 1000)
        self.assertTrue(ts1 == ts2)

    def test_today(self):
        ts1 = default_from('today()')
        tmp = dt.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ts2 = int((tmp - self.epoch).total_seconds() * 1000)
        self.assertTrue(ts1 == ts2)

    def test_yesterday(self):
        ts1 = default_from('yesterday()')
        tmp = dt.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ts2 = int((tmp - self.epoch).total_seconds() * 1000) - 86400000
        self.assertTrue(ts1 == ts2)


if __name__ == '__main__':
    unittest.main()
