import datetime
import pathlib
from typing import Callable

import isoweek
import yaml
from typing import Any

from time_report import database

HOME_DIR = pathlib.Path().home() / 'time_report'

SETTINGS_PATH = HOME_DIR / "settings.yaml"


class Settings:
    def __init__(self):
        self._data = {}
        self._callbacks: list[Callable] = []
        self.load_settings()

    def __getitem__(self, item: str):
        return self._data.get(item)

    def __setitem__(self, key: str, value: Any):
        self._data[key] = value

    def load_settings(self):
        if not SETTINGS_PATH.exists():
            return
        with open(SETTINGS_PATH) as fid:
            self._data = yaml.safe_load(fid)

    def save_settings(self) -> None:
        with open(SETTINGS_PATH, 'w') as fid:
            yaml.safe_dump(self._data, fid)
        self._trigger_callbacks()

    def add_callback(self, func: Callable) -> None:
        self._callbacks.append(func)

    @property
    def data(self) -> dict:
        return self._data

    @property
    def _this_year(self) -> int:
        return datetime.datetime.now().year

    @property
    def _this_week(self) -> isoweek.Week:
        return isoweek.Week.thisweek()

    @property
    def year(self) -> int:
        return self._data.get("year", self._this_year)

    @year.setter
    def year(self, year: int) -> None:
        self._data["year"] = year
        self.save_settings()

    @property
    def week(self) -> isoweek.Week:
        week = self._this_week
        week_nr = self._data.get("week")
        if week_nr:
            week = isoweek.Week(self.year, int(week_nr))
        return week

    @week.setter
    def week(self, week: int | str | isoweek.Week) -> None:
        if isinstance(week, isoweek.Week):
            week = week.week
        self._data["week"] = int(week)
        self.save_settings()

    @property
    def first_week_of_year(self) -> isoweek.Week:
        """Returns "first" week och active year. """
        week_nr = self._data.get("first_week_of_year", {}).get(self.year)
        if week_nr:
            return isoweek.Week(self.year, int(week_nr))
        return isoweek.Week(self.year, 1)

    @first_week_of_year.setter
    def first_week_of_year(self, week: str | int | isoweek.Week) -> None:
        if isinstance(week, isoweek.Week):
            week = week.week
        self._data.setdefault("first_week_of_year", {})
        self._data["first_week_of_year"][self.year] = int(week)
        self.save_settings()

    @property
    def first_date_of_year(self) -> datetime.date:
        return self.first_week_of_year.days()[0]

    @property
    def last_week_of_year(self) -> isoweek.Week:
        """Returns "last" week och active year. """
        week_nr = self._data.get("last_week_of_year", {}).get(self.year)
        if week_nr:
            return isoweek.Week(self.year, int(week_nr))
        return list(isoweek.Week.weeks_of_year(self.year))[-1]

    @last_week_of_year.setter
    def last_week_of_year(self, week: str | int | isoweek.Week) -> None:
        if isinstance(week, isoweek.Week):
            week = week.week
        self._data.setdefault("last_week_of_year", {})
        self._data["last_week_of_year"][self.year] = int(week)
        self.save_settings()

    @property
    def last_date_of_year(self) -> datetime.date:
        return self.last_week_of_year.days()[-1]

    @property
    def weeks_of_year(self) -> list[isoweek.Week]:
        from_week_nr = self.first_week_of_year.week
        to_week_nr = self.last_week_of_year.week
        weeks = []
        for week in isoweek.Week.weeks_of_year(self.year):
            if week.week < from_week_nr:
                continue
            if week.week > to_week_nr:
                continue
            weeks.append(week)
        return weeks

    def get_year_list(self) -> list[int]:
        years = set([obj.date.year for obj in database.get_dates_info()])
        this_year = self._this_year
        years.add(this_year)
        years.add(this_year + 1)
        return sorted(years)

    def _trigger_callbacks(self):
        for func in self._callbacks:
            func(self._data)

    @property
    def not_current_week_alert_bgcolor(self) -> str:
        return self._data.get("not_current_week_alert_bgcolor", "red")

    @not_current_week_alert_bgcolor.setter
    def not_current_week_alert_bgcolor(self, bgcolor: str) -> None:
        if not isinstance(bgcolor, str):
            raise ValueError("Not a valid background color")
        self._data["not_current_week_alert_bgcolor"] = bgcolor
        self.save_settings()


settings = Settings()
