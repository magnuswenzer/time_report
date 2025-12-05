from time_report import utils
import datetime


def test_timedelta_hour():
    dt = datetime.timedelta(hours=2)
    td = utils.TimeDelta(dt)
    assert td.hours == 2
    assert td.dt == dt


def test_timedelta_minutes():
    dt = datetime.timedelta(minutes=20)
    td = utils.TimeDelta(dt)
    assert td.minutes == 20
    assert td.dt == dt


def test_timedelta_hour_and_minutes():
    dt = datetime.timedelta(hours=2, minutes=20)
    td = utils.TimeDelta(dt)
    assert td.hours == 2
    assert td.minutes == 20
    assert td.dt == dt


def test_timedelta_negative_hour():
    dt = datetime.timedelta(hours=-3)
    td = utils.TimeDelta(dt)
    assert td.hours == -3
    assert td.dt == dt
    assert td.tot_minutes == (-60 * 3)
    assert td.tot_hours == -3


def test_timedelta_negative_minutes():
    dt = datetime.timedelta(minutes=-30)
    td = utils.TimeDelta(dt)
    assert td.minutes == -30
    assert td.dt == dt


def test_timedelta_negative_hours_and_minutes():
    dt = datetime.timedelta(hours=-3, minutes=-30)
    td = utils.TimeDelta(dt)
    assert td.hours == -3
    assert td.minutes == -30
    assert td.dt == dt


def test_timedelta_negative_hours_and_positive_minutes():
    dt = datetime.timedelta(hours=-3, minutes=10)
    td = utils.TimeDelta(dt)
    assert td.hours == -2
    assert td.minutes == -50
    assert td.dt == dt
    assert td.tot_minutes == (-50 -60 * 2)


def test_timedelta_positive_hours_and_negative_minutes():
    dt = datetime.timedelta(hours=4, minutes=-5)
    td = utils.TimeDelta(dt)
    assert td.hours == 3
    assert td.minutes == 55
    assert td.dt == dt
    assert td.tot_minutes == (60 * 4 - 5)




