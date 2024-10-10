import datetime

import flet as ft
from time_report import database, controller


class PageDayReport(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self._btn_pick_date = ft.ElevatedButton(
            datetime.datetime.now().strftime('%Y-%m-%d'),
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda e: self.page.open(self._date_picker),
        )

        self._date_picker = ft.DatePicker(
            first_date=datetime.datetime(year=datetime.datetime.now().year, month=1, day=1),
            last_date=datetime.datetime(year=datetime.datetime.now().year, month=12, day=31),
            on_change=self._on_change_date,
            confirm_text='Välj',
            cancel_text='Avbryt',
            help_text='Välj datum'
        )

        self._table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Project")),
                ft.DataColumn(ft.Text("Timmar"), numeric=True),
                ft.DataColumn(ft.Text("Minuter"), numeric=True),
            ],
        )
        self._set_table()

        self.controls = [
            self._btn_pick_date,
            self._table
        ]

    def _on_change_date(self, e):
        self._btn_pick_date.text = e.control.value.strftime('%Y-%m-%d')
        self._btn_pick_date.update()

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.strptime(self._btn_pick_date.text, '%Y-%m-%d')

    def _set_table(self) -> None:
        rows = []
        for proj in database.get_projects():
            td = controller.get_total_time_for_project_and_day(proj, self.datetime)
            if not td:
                continue
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(proj.name)),
                        ft.DataCell(ft.Text(str(td.hours))),
                        ft.DataCell(ft.Text(str(td.minutes))),
                    ],
                ),
            )
            self._table.rows = rows

    def update_page(self) -> None:
        self._set_table()
        self.update()




