import datetime

import flet as ft
from time_report import database, controller
from time_report import utils


class PageWeekSchedule(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self._weekday_fields = {
            0: ft.TextField(label='Måndag'),
            1: ft.TextField(label='Tisdag'),
            2: ft.TextField(label='Onsdag'),
            3: ft.TextField(label='Tordag'),
            4: ft.TextField(label='Fredag'),
            5: ft.TextField(label='Lördag'),
            6: ft.TextField(label='Söndag'),
        }

        options = []
        for w in range(1, 54):
            options.append(ft.dropdown.Option(str(w)))

        self._week_dropdown = ft.Dropdown(
            label="Vecka",
            hint_text="Välj en vecka",
            autofocus=False,
            on_change=self._on_change_week,
            options=options
        )

        self._week_dropdown.value = datetime.datetime.now().strftime('%W')

        self.controls = [
            self._week_dropdown,
            ft.Column([t for t in self._weekday_fields.values()])
        ]

    @property
    def week(self) -> int:
        return int(self._week_dropdown.value)

    def _on_change_week(self, *args):
        self.update()

    def update_page(self) -> None:
        self._on_change_week()




