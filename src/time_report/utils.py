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

SECONDS_IN_A_MINUTE = 60
SECONDS_IN_AN_HOUR = SECONDS_IN_A_MINUTE * 60
SECONDS_IN_A_DAY = SECONDS_IN_AN_HOUR * 24


class TimeDelta:

    def __init__(self, dt: datetime.timedelta | None = None):
        self._dt = dt or datetime.timedelta()

    def __repr__(self):
        string = f'{abs(self.hours)}:{str(abs(self.minutes)).zfill(2)}'
        if self._sign_factor == -1:
            string = f'-{string}'
        if self.seconds:
            string = f'{string}:{str(abs(self.seconds)).zfill(2)}'
        return string
        # return self._dt.__repr__()

    def __add__(self, other):
        return TimeDelta(self._dt + other.dt)

    def __sub__(self, other):
        return TimeDelta(self._dt - other.dt)

    # def _fix_sign(self, value: int) -> int:
    #     if self._dt == self.dt:
    #         return value
    #     return -value

    @property
    def dt(self) -> datetime.timedelta:
        if self._dt < datetime.timedelta():
            return -self._dt
        return self._dt

    @property
    def tot_seconds(self) -> int:
        seconds_from_days = self._dt.days * SECONDS_IN_A_DAY
        return seconds_from_days + self._dt.seconds

    @property
    def tot_hours(self) -> float:
        return self.tot_seconds / SECONDS_IN_AN_HOUR

    @property
    def tot_minutes(self) -> float:
        return self.tot_seconds / SECONDS_IN_A_MINUTE

    @property
    def hours(self) -> int:
        return (abs(self.tot_seconds) // SECONDS_IN_AN_HOUR) * self._sign_factor

    @property
    def minutes(self) -> int:
        return (abs(self.tot_seconds) % SECONDS_IN_AN_HOUR // SECONDS_IN_A_MINUTE) * self._sign_factor

    @property
    def seconds(self) -> int:
        return (abs(self.tot_seconds) % SECONDS_IN_A_DAY % SECONDS_IN_AN_HOUR % SECONDS_IN_A_MINUTE) * self._sign_factor


    @property
    def _sign_factor(self) -> int:
        if self.tot_seconds < 0:
            return -1
        return 1

    # @property
    # def hours(self) -> int:
    #     hours = 24 * self._dt.days
    #     return hours + (self._dt.seconds // 3600)
    #
    # @property
    # def minutes(self) -> int:
    #     return self._dt.seconds % 3600 // 60


def get_week_range(week: int | str) -> list[datetime.datetime]:
    d = f"{datetime.datetime.now().year}-{week}"
    start = datetime.datetime.strptime(d + '-1', "%Y-%W-%w")
    stop = start + datetime.timedelta(days=8, seconds=-1)
    return [start, stop]


def get_week_dates(week: int | str) -> list[datetime.date]:
    d = f"{datetime.datetime.now().year}-{week}"
    start = datetime.datetime.strptime(d + '-1', "%Y-%W-%w")
    lst = [start.date()]
    for d in range(1, 7):
        new_date = start + datetime.timedelta(days=d)
        lst.append(new_date.date())
        #lst.append(start + datetime.timedelta(days=d))
    return lst


def get_day_range(dtime: datetime.datetime | datetime.date) -> list[datetime.datetime]:
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
