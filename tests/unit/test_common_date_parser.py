from datetime import datetime as dt

import pytest

from devo.common import default_from, default_to


@pytest.fixture(scope="module")
def setup_epoch():
    epoch = dt.utcfromtimestamp(0)
    yield epoch


# Tests defaults
# --------------------------------------------------------------------------
def test_default_to(setup_epoch):
    ts1 = str(default_to())[:11]
    ts2 = str((dt.utcnow() - setup_epoch).total_seconds() * 1000)[:11]
    assert ts1 == ts2


def test_default_from(setup_epoch):
    ts1 = str(default_from())[:11]
    ts2 = str(int((dt.utcnow() - setup_epoch).total_seconds() * 1000) - 86400000)[:11]
    assert ts1 == ts2


# Tests amounts
# --------------------------------------------------------------------------
def test_second():
    assert default_from("second()") == 1000


def test_minute():
    assert default_from("minute()") == 60 * 1000


def test_hour():
    assert default_from("hour()") == 60 * 60 * 1000


def test_day():
    assert default_from("day()") == 24 * 60 * 60 * 1000


def test_week():
    assert default_from("week()") == 7 * 24 * 60 * 60 * 1000


def test_month():
    assert default_from("month()") == 30 * 24 * 60 * 60 * 1000


# Tests relatives
# --------------------------------------------------------------------------
def test_now(setup_epoch):
    assert default_from("now()") == int((dt.utcnow() - setup_epoch).total_seconds() * 1000)


def test_today(setup_epoch):
    tmp = dt.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    assert default_from("today()") == int((tmp - setup_epoch).total_seconds() * 1000)


def test_yesterday(setup_epoch):
    tmp = dt.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    assert (
        default_from("yesterday()") == int((tmp - setup_epoch).total_seconds() * 1000) - 86400000
    )


if __name__ == "__main__":
    pytest.main()
