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

DATE_FORMAT = '%Y-%m-%d'


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


def get_red_dates(year: int) -> list[datetime.date]:
    month_day = [
        (1, 1),
        (1, 6),
        (3, 29),
        (3, 30),
        (3, 31),
        (4, 1),
        (5, 1),
        (5, 9),
        (5, 19),
        (5, 20),
        (6, 6),
        (6, 21),
        (6, 22),
        (11, 2),
        (12, 24),
        (12, 25),
        (12, 26),
        (12, 31),
    ]
    date_lst = []
    for m, d in month_day:
        date_lst.append(datetime.datetime(year, m, d).date())
    return date_lst
