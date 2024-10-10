import datetime

WEEKDAYS = [
    'Måndag',
    'Tisdag',
    'Onsdag',
    'Torsdag',
    'Fredag',
    'Lördag',
    'Söndag'
]


class TimeDelta:

    def __init__(self, dt: datetime.timedelta | None = None):
        self.dt = dt or datetime.timedelta()

    def __repr__(self):
        return self.dt.__repr__()

    def __add__(self, other):
        return TimeDelta(self.dt + other.dt)

    @property
    def seconds(self) -> int:
        return self.dt.seconds

    @property
    def hours(self) -> int:
        return self.seconds // 3600

    @property
    def minutes(self) -> int:
        return (self.seconds % 3600) // 60


def get_week_range(week: int | str) -> list[datetime.datetime]:
    d = f"{datetime.datetime.now().year}-{week}"
    start = datetime.datetime.strptime(d + '-1', "%Y-%W-%w")
    stop = start + datetime.timedelta(days=8, seconds=-1)
    return [start, stop]


def get_week_dates(week: int | str) -> list[datetime.datetime]:
    d = f"{datetime.datetime.now().year}-{week}"
    start = datetime.datetime.strptime(d + '-1', "%Y-%W-%w")
    lst = [start]
    for d in range(1, 7):
        lst.append(start + datetime.timedelta(days=d))
    return lst


def get_day_range(dtime: datetime.datetime) -> list[datetime.datetime]:
    start_of_day = datetime.datetime(dtime.year, dtime.month, dtime.day)
    end_of_day = start_of_day + datetime.timedelta(days=1, seconds=-1)
    return [start_of_day, end_of_day]
