import calendar
from datetime import datetime, timedelta

import pytest
import pytz

from devo.api import Client


def test_from_Date_Days():
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._fromDate_parser("2d", now)
    now_miliseconds = now.timestamp() * 1000
    assert response_miliseconds == now_miliseconds - 1.728e8


def test_from_absolute_date_Days():
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._fromDate_parser("2ad", now)
    adate_miliseconds = (
        datetime.strptime(str(now.date()), "%Y-%m-%d").replace(tzinfo=pytz.utc).timestamp() * 1000
    )
    assert response_miliseconds == adate_miliseconds - 1.728e8


def test_from_date_hours():
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._fromDate_parser("2h", now)
    now_miliseconds = now.timestamp() * 1000
    assert response_miliseconds == now_miliseconds - 7.2e6


def test_from_absolute_date_hours():
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._fromDate_parser("2ah", now)
    adate_miliseconds = (
        datetime.strptime(str(now.date()), "%Y-%m-%d").replace(tzinfo=pytz.utc).timestamp() * 1000
    )
    assert response_miliseconds == adate_miliseconds - 7.2e6


def test_from_date_minutes():
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._fromDate_parser("2m", now)
    now_miliseconds = now.timestamp() * 1000
    assert response_miliseconds == now_miliseconds - 120000


def test_from_absolute_date_minutes():
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._fromDate_parser("2am", now)
    adate_miliseconds = (
        datetime.strptime(str(now.date()), "%Y-%m-%d").replace(tzinfo=pytz.utc).timestamp() * 1000
    )
    assert response_miliseconds == adate_miliseconds - 120000


def test_from_date_seconds():
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._fromDate_parser("2s", now)
    now_miliseconds = now.timestamp() * 1000
    assert response_miliseconds == now_miliseconds - 2000


def test_from_absolute_date_seconds():
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._fromDate_parser("2as", now)
    adate_miliseconds = (
        datetime.strptime(str(now.date()), "%Y-%m-%d").replace(tzinfo=pytz.utc).timestamp() * 1000
    )
    assert response_miliseconds == adate_miliseconds - 2000


def test_from_today_date():
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._fromDate_parser("today", now)
    adate_miliseconds = (
        datetime.strptime(str(now.date()), "%Y-%m-%d").replace(tzinfo=pytz.utc).timestamp() * 1000
    )
    assert response_miliseconds == adate_miliseconds


def test_from_endday_date():
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._fromDate_parser("endday", now)
    adate_miliseconds = (
        datetime.strptime(str(now.date()), "%Y-%m-%d").replace(tzinfo=pytz.utc)
        + timedelta(hours=23, minutes=59, seconds=59)
    ).timestamp() * 1000
    assert response_miliseconds == adate_miliseconds


def test_from_endmonth_date():
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._fromDate_parser("endmonth", now)
    adate = datetime.strptime(str(now.date()), "%Y-%m-%d").replace(tzinfo=pytz.utc)
    adate_miliseconds = (
        adate.replace(day=calendar.monthrange(adate.year, adate.month)[1])
        + timedelta(hours=23, minutes=59, seconds=59)
    ).timestamp() * 1000
    assert response_miliseconds == adate_miliseconds


def test_from_now_date():
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._fromDate_parser("now", now)
    assert response_miliseconds == now.timestamp() * 1000


# FromDate in ms (1663664778239.2002) corresponds to "Tue Sep 20 2022 09:06:18 UTC"
# FromDate in ms Absolute (1663632000000) corresponds to "Tue Sep 20 2022 00:00:00 UTC"
def test_to_Date_Days():
    fromDateMiliseconds = 1663664778239.2002
    response_miliseconds = Client._toDate_parser(fromDateMiliseconds, "2d")
    assert response_miliseconds == fromDateMiliseconds + 1.728e8


def test_to_Date_absolute_Days():
    fromDateMiliseconds = 1663664778239.2002
    fromDateMilisecondsAbsolute = 1663632000000
    response_miliseconds = Client._toDate_parser(fromDateMiliseconds, "2ad")
    assert response_miliseconds == fromDateMilisecondsAbsolute + 1.728e8


def test_to_Date_hours():
    fromDateMiliseconds = 1663664778239.2002
    response_miliseconds = Client._toDate_parser(fromDateMiliseconds, "2h")
    assert response_miliseconds == fromDateMiliseconds + 7.2e6


def test_to_Date_absolute_hours():
    fromDateMiliseconds = 1663664778239.2002
    fromDateMilisecondsAbsolute = 1663632000000
    response_miliseconds = Client._toDate_parser(fromDateMiliseconds, "2ah")
    assert response_miliseconds == fromDateMilisecondsAbsolute + 7.2e6


def test_to_Date_minutes():
    fromDateMiliseconds = 1663664778239.2002
    response_miliseconds = Client._toDate_parser(fromDateMiliseconds, "2m")
    assert response_miliseconds == fromDateMiliseconds + 120000


def test_to_Date_absolute_minutes():
    fromDateMiliseconds = 1663664778239.2002
    fromDateMilisecondsAbsolute = 1663632000000
    response_miliseconds = Client._toDate_parser(fromDateMiliseconds, "2am")
    assert response_miliseconds == fromDateMilisecondsAbsolute + 120000


def test_to_Date_seconds():
    fromDateMiliseconds = 1663664778239.2002
    response_miliseconds = Client._toDate_parser(fromDateMiliseconds, "2s")
    assert response_miliseconds == fromDateMiliseconds + 2000


def test_to_Date_absolute_seconds():
    fromDateMiliseconds = 1663664778239.2002
    fromDateMilisecondsAbsolute = 1663632000000
    response_miliseconds = Client._toDate_parser(fromDateMiliseconds, "2as")
    assert response_miliseconds == fromDateMilisecondsAbsolute + 2000


def test_to_Date_today():
    fromDateMiliseconds = 1663664778239.2002
    now = datetime.now().astimezone(pytz.UTC)
    aNowdate = datetime.strptime(str(now.date()), "%Y-%m-%d").replace(tzinfo=pytz.utc)
    response_miliseconds = Client._toDate_parser(fromDateMiliseconds, "today", now)

    assert response_miliseconds == aNowdate.timestamp() * 1000


def test_to_Date_endday():
    fromDateMiliseconds = 1663664778239.2002
    response = 1663718399000  # Corresponds to Tue Sep 20 2022 23:59:59
    response_miliseconds = Client._toDate_parser(fromDateMiliseconds, "endday")

    assert response_miliseconds == response


def test_to_Date_endmonth():
    fromDateMiliseconds = 1663664778239.2002
    response = 1664582399000  # Corresponds to Fri Sep 30 2022 23:59:59
    response_miliseconds = Client._toDate_parser(fromDateMiliseconds, "endmonth")

    assert response_miliseconds == response


def test_to_Date_now():
    fromDateMiliseconds = 1663664778239.2002
    now = datetime.now().astimezone(pytz.UTC)
    response_miliseconds = Client._toDate_parser(fromDateMiliseconds, "now", now)

    assert response_miliseconds == now.timestamp() * 1000


if __name__ == "__main__":
    pytest.main()
