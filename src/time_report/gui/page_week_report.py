import datetime

import flet as ft
from time_report import database, controller
from time_report import utils


class PageWeekReport(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self._week_dates = []

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

        self._header_texts = []
        columns = [ft.DataColumn(ft.Text("Projekt"))]
        for _ in range(7):
            text = ft.Text()
            columns.append(ft.DataColumn(text))
            self._header_texts.append(text)
        columns.append(ft.DataColumn(ft.Text("TOTALT")))

        self._table = ft.DataTable(
            columns=columns,
        )
        self._update_header(update=False)

        self.controls = [
            self._week_dropdown,
            self._table
        ]

    @property
    def week(self) -> int:
        return int(self._week_dropdown.value)

    def _on_change_week(self, *args):
        self._update_week_days()
        self._update_header()
        self._update_hours_in_table()
        self.update()

    def _update_week_days(self):
        self._week_dates = utils.get_week_dates(self.week)

    def _update_header(self, update: bool = True):
        for d, text, wd in zip(self._week_dates, self._header_texts, utils.WEEKDAYS):
            text.value = f'{wd}\n{d.strftime('%Y-%m-%d')}'
            if update:
                text.update()

    def _update_hours_in_table(self):
        rows = []
        for proj in database.get_projects():
            week_td = controller.get_total_time_for_project_and_week(proj, self.week)
            if not week_td:
                continue
            cells = []
            cells.append(ft.DataCell(ft.Text(proj.name)))
            for date in self._week_dates:
                text = ''
                td = controller.get_total_time_for_project_and_day(proj, date)
                if td:
                    text = f'{td.hours}:{str(td.minutes).zfill(2)}'
                cells.append(ft.DataCell(ft.Text(text)))
            text = f'{week_td.hours}:{str(week_td.minutes).zfill(2)}'
            cells.append(ft.DataCell(ft.Text(text)))
            rows.append(
                ft.DataRow(
                    cells=cells,
                ),
            )
        total_cells = [ft.DataCell(ft.Text('TOTALT'))]
        tot_td = utils.TimeDelta()
        for date in self._week_dates:
            text = ''
            td = controller.get_total_time_for_day(date)
            if td:
                text = f'{td.hours}:{str(td.minutes).zfill(2)}'
                tot_td += td
            total_cells.append(ft.DataCell(ft.Text(text)))
        text = f'{tot_td.hours}:{str(tot_td.minutes).zfill(2)}'
        total_cells.append(ft.DataCell(ft.Text(text)))
        rows.append(
            ft.DataRow(
                cells=total_cells,
            ),
        )
        self._table.rows = rows

    def update_page(self) -> None:
        self._on_change_week()




