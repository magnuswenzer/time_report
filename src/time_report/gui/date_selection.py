import flet as ft
import datetime

import isoweek

from time_report import controller, utils
from time_report.settings import settings


class DateSelection(ft.Column):

    def __init__(self, callback_change_date):
        super().__init__()

        label_width = 300

        self._callback_change_date = callback_change_date

        self._date_picker = ft.DatePicker(
            first_date=datetime.datetime(year=settings.year, month=1, day=1),
            last_date=datetime.datetime.now(),
            # last_date=datetime.datetime(year=datetime.datetime.now().year, month=12, day=31),
            on_change=self._on_change_manual_date,
            confirm_text='Välj',
            cancel_text='Avbryt',
            help_text='Välj datum'
            # on_dismiss=self._on_discard_manual_date,
        )

        self._btn_pick_date = ft.ElevatedButton(
            datetime.datetime.now().strftime('%Y-%m-%d'),
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda e: self.page.open(self._date_picker),
        )

        self.controls = [
            ft.Row([
                self._btn_pick_date,
                ft.ElevatedButton('Idag', on_click=self._goto_today),
                ft.ElevatedButton('Gå till sista rapporterade dag',
                                  on_click=self._goto_last_reported_day),
            ]),
        ]

    @property
    def value(self) -> str:
        return self._btn_pick_date.text

    @property
    def date(self) -> datetime.date | None:
        date_str = self.value
        if not date_str:
            return
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    @date.setter
    def date(self, date: datetime.date) -> None:
        self._btn_pick_date.text = date.strftime('%Y-%m-%d')
        self._btn_pick_date.update()
        self._on_change_date()

    def _on_change_manual_date(self, e):
        self.date = e.control.value
        # self._btn_pick_date.text = e.control.value.strftime('%Y-%m-%d')
        # self._btn_pick_date.update()

    def _on_change_date(self, *args):
        self._callback_change_date()

    def _goto_today(self, *args):
        self.date = datetime.datetime.now().date()

    def _goto_last_reported_day(self, *args):
        latest_sub = controller.get_latest_submitted_time()
        self.date = utils.get_last_date_of_week(date=latest_sub.date)

