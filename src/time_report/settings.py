import datetime
import pathlib
from typing import Callable

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
        self._trigger_callbacks()
        with open(SETTINGS_PATH, 'w') as fid:
            yaml.safe_dump(self._data, fid)

    def add_callback(self, func: Callable) -> None:
        self._callbacks.append(func)

    @property
    def data(self) -> dict:
        return self._data

    @property
    def this_year(self) -> int:
        return datetime.datetime.now().year

    @property
    def year(self) -> int:
        return self._data.get("year", self.this_year)

    @year.setter
    def year(self, year: int) -> None:
        self._data["year"] = year
        self.save_settings()

    def get_year_list(self) -> list[int]:
        years = set([obj.date.year for obj in database.get_dates_info()])
        this_year = self.this_year
        years.add(this_year)
        years.add(this_year + 1)
        return sorted(years)

    def _trigger_callbacks(self):
        for func in self._callbacks:
            func(self._data)


settings = Settings()
