import datetime
import pathlib

import isoweek
import pandas as pd
from time_report.settings import settings


WEEKDAYS = [
    'Måndag',
    'Tisdag',
    'Onsdag',
    'Torsdag',
    'Fredag',
    'Lördag',
    'Söndag'
]

HOME_DIR = pathlib.Path().home() / 'time_report'

SETTINGS_PATH = HOME_DIR / "settings.yaml"

DATE_FORMAT = '%Y-%m-%d'

SECONDS_IN_A_MINUTE = 60
SECONDS_IN_AN_HOUR = SECONDS_IN_A_MINUTE * 60
SECONDS_IN_A_DAY = SECONDS_IN_AN_HOUR * 24


weekday_mapping = dict((i, wd) for i, wd in enumerate(WEEKDAYS))


def _get_red_dates_file_path(year: int) -> pathlib.Path:
    return HOME_DIR / f'red_dates_{year}.txt'


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

    def __eq__(self, other):
        return self.dt == other.dt

    def __add__(self, other):
        # return TimeDelta(self.dt + other.dt)
        return TimeDelta(self._dt + other._dt)
        # return TimeDelta(self._dt + other.dt)

    def __sub__(self, other):
        # return TimeDelta(self.dt - other.dt)
        return TimeDelta(self._dt - other._dt)
        # return TimeDelta(self._dt - other.dt)

    # def _fix_sign(self, value: int) -> int:
    #     if self._dt == self.dt:
    #         return value
    #     return -value

    @property
    def dt(self) -> datetime.timedelta:
        return self._dt
        # if self._dt < datetime.timedelta():
        #     return -self._dt
        # return self._dt

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


class RedDate:

    def __init__(self,
                 name: str = None,
                 date: datetime.datetime = None,
                 week_day: str = "",
                 **kwargs
                 ):
        self.name = name
        self.date = date
        self.week = isoweek.Week.withdate(self.date)
        self.week_day = week_day
        self.year = self.date.year
        self._kwargs = kwargs

    # def __init__(self, series: pd.Series):
    #     self._series = series
    #     self.name = series.Namn
    #     self.date = datetime.datetime.strptime(series.Datum, '%Y-%m-%d').date()
    #     self.week = isoweek.Week.withdate(self.date)
    #     self.week_day = series.Veckodag
    #     self.year = self.date.year

    def __str__(self):
        return f'{self.date} ({self.name})'

    def __lt__(self, other):
        return self.date <= other.date

    @classmethod
    def from_series(cls, series: pd.Series):
        data = dict()
        data["series"] = series
        data["name"] = series.Namn
        data["date"] = datetime.datetime.strptime(series.Datum, '%Y-%m-%d').date()
        data["week"] = isoweek.Week.withdate(data["date"])
        data["week_day"] = series.Veckodag
        data["year"] = data["date"].year
        return RedDate(**data)


class RedDates:

    def __init__(self, data: pd.DataFrame):
        self._df = data
        self._date_objects: list[RedDate] = []
        self._load_data()

    def _load_data(self):
        self._date_objects = []
        for i, series in self._df.iterrows():
            rd = RedDate.from_series(series)
            if rd.date.month == 12 and rd.date.day == 25:
                extra_rd = RedDate(
                    name="Julafton",
                    date=rd.date - datetime.timedelta(days=1)
                )
                self._date_objects.append(extra_rd)
            self._date_objects.append(rd)
            if rd.name.lower() == 'midsommardagen':
                extra_rd = RedDate(
                    name="Midsommarafton",
                    date=rd.date - datetime.timedelta(days=1)
                )
                self._date_objects.append(extra_rd)

    def get_dates(self, year: int = None) -> list[datetime.date]:
        dates = []
        for obj in self._date_objects:
            if year is not None and obj.year != year:
                continue
            dates.append(obj.date)
        return dates


def old_get_week_range(week: int | str) -> list[datetime.datetime]:
    d = f"{settings.year}-{int(week) - 1}"
    start = datetime.datetime.strptime(d + '-1', "%Y-%W-%w")
    stop = start + datetime.timedelta(days=7, seconds=-1)
    return [start, stop]


def get_week_for_date(date: datetime.date) -> isoweek.Week:
    return isoweek.Week.withdate(date)


def get_date_range(date_start: datetime.date,
                   date_stop: datetime.date) -> list[datetime.date]:
    dates = []
    date = date_start
    while True:
        dates.append(date)
        date = date + datetime.timedelta(days=1)
        if date > date_stop:
            break
    return dates


def get_week_range(week: int | str) -> list[datetime.datetime]:
    days = isoweek.Week(settings.year, int(week)).days()
    return [days[0], days[-1]]


def get_weeks_for_year(year: int) -> list[isoweek.Week]:
    return list(isoweek.Week.weeks_of_year(year))


def old_get_week_dates(week: int | str) -> list[datetime.date]:
    d = f"{settings.year}-{int(week) - 1}"
    start = datetime.datetime.strptime(d + '-1', "%Y-%W-%w")
    lst = [start.date()]
    for d in range(1, 7):
        new_date = start + datetime.timedelta(days=d)
        lst.append(new_date.date())
        #lst.append(start + datetime.timedelta(days=d))
    return lst


def get_week_dates(week: int | str) -> list[datetime.date]:
    return isoweek.Week(settings.year, int(week)).days()


def get_first_date_of_week(week: int | str) -> datetime.date:
    return get_week_dates(week)[0]


def get_last_date_of_week(week: int | str = None,
                          date: datetime.date = None) -> datetime.date:
    if date:
        return get_week_for_date(date).days()[-1]
    return get_week_dates(week)[-1]


def get_day_range(dtime: datetime.datetime | datetime.date) -> list[datetime.datetime]:
    start_of_day = datetime.datetime(dtime.year, dtime.month, dtime.day)
    end_of_day = start_of_day + datetime.timedelta(days=1, seconds=-1)
    return [start_of_day, end_of_day]


def get_first_date_of_year() -> datetime.date:
    """Returns 1 jan of selected year or first day of the first wek of current year"""
    settings.year



def old_get_red_dates(year: int) -> list[datetime.date]:
    month_day = [
        (1, 1),
        (1, 6),
        (4, 18),
        (4, 20),
        (5, 1),
        (5, 29),
        (6, 6),
        (6, 20),
        (6, 21),
        (11, 1),
        (12, 24),
        (12, 25),
        (12, 26),
        (12, 31),
    ]
    date_lst = []
    for m, d in month_day:
        date_lst.append(datetime.datetime(year, m, d).date())
    return date_lst


def get_red_dates() -> RedDates:
    year = settings.year
    dfs = []
    for y in range(year-1, year+2):
        path = _get_red_dates_file_path(y)
        if not path.exists():
            _download_red_dates(y)
        df = pd.read_csv(path, sep='\t')
        dfs.append(df)
    tot_df = pd.concat(dfs)
    # df = pd.read_csv(path, sep='\t')
    return RedDates(tot_df)


def _download_red_dates(year: int):
    try:
        dfs = pd.read_html(f'https://kalender.se/helgdagar/{year}')
        df = dfs[0]
        df.to_csv(_get_red_dates_file_path(year), sep='\t', index=False)
    except:
        print(f'Could not download red dates for year: {year}')


def get_h_str(tdelta: TimeDelta) -> str:
    return str(tdelta).split(":")[0]


def get_hm_str(tdelta: TimeDelta) -> str:
    return str(tdelta).rsplit(":", 1)[0]


if __name__ == '__main__':
    # dt_pos = TimeDelta(datetime.timedelta(minutes=15))
    # dt_neg = TimeDelta(datetime.timedelta(minutes=-10))
    dates = get_red_dates()

    dfs = pd.read_html('https://kalender.se/helgdagar')
    df = dfs[0]

    red = get_red_dates().get_dates(settings.year)

