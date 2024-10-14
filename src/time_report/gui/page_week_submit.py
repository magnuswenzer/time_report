import datetime

import flet as ft
from time_report import database, controller
from time_report import utils
from time_report.gui import week_selection


class PageWeekSubmit(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self._week_dates = []

        self.week_selection = week_selection.WeekSelection(callback_change_week=self._on_change_week)

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
            self.week_selection,
            self._table,
            ft.ElevatedButton('Rapportera tid', on_click=self._submit)
        ]

    @property
    def week(self) -> int:
        return int(self.week_selection.value)

    @property
    def week_dates(self) -> list[datetime.date]:
        return utils.get_week_dates(self.week)

    @property
    def latest_date(self) -> datetime.date:
        return min([datetime.datetime.now().date(), self.week_dates[-1]])

    def _on_change_week(self, *args):
        self._update_week_days()
        self._update_header()
        self._update_hours_in_table()
        self._set_suggestion_in_fields() ###NEW
        self._on_change_field()
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
        self._fields = {}
        self._date_sum = {}
        self._proj_sum = {}
        self._tot_sum = None
        for proj in database.get_projects():
            week_td = controller.get_total_time_for_project_and_week(proj, self.week)
            if not week_td:
                continue
            self._fields[proj.name] = {}
            cells = []
            cells.append(ft.DataCell(ft.Text(proj.name)))
            for d, date in enumerate(self._week_dates):
                label = ''
                td = controller.get_total_time_for_project_and_day(proj, date)
                if td:
                    label = str(td.hours)
                field = ft.TextField(
                    on_change=self._on_change_field,
                    input_filter=ft.NumbersOnlyInputFilter()
                )
                field.label = label
                self._fields[proj.name][d] = field
                cells.append(ft.DataCell(field))
            text = ft.Text()
            self._proj_sum[proj.name] = text
            cells.append(ft.DataCell(text))
            rows.append(
                ft.DataRow(
                    cells=cells,
                ),
            )
        total_cells = [ft.DataCell(ft.Text('TOTALT'))]
        for d, date in enumerate(self._week_dates):
            text = ft.Text(text)
            self._date_sum[d] = text
            total_cells.append(ft.DataCell(text))
        text = ft.Text()
        self._tot_sum = text
        total_cells.append(ft.DataCell(text))
        rows.append(
            ft.DataRow(
                cells=total_cells,
            ),
        )
        self._table.rows = rows

    def _set_suggestion_in_fields(self) -> None:
        tot_sum = self._get_tot_sum()
        tot_scheduled_time = controller.get_sum_of_scheduled_time(date_start=self.week_dates[0], date_stop=self.week_dates[-1])
        for proj_name, value in self._get_time_diff_for_projects().items():
            hour_diff = value['diff'].hours
            if not hour_diff:
                continue
            for i, (d, field) in enumerate(self._fields[proj_name].items()):
                if tot_sum == tot_scheduled_time:
                    break
                if not hour_diff:
                    continue
                current_field_value_str = field.value or field.label
                current_field_value = int(current_field_value_str or 0)
                date = self.week_dates[i]
                date_info = controller.get_date_info(date)
                max_nr_hours = utils.TimeDelta(date_info.time_in_plan).hours
                print()
                print('='*100)
                print(proj_name)
                print('-'*100)
                while current_field_value < max_nr_hours:
                    current_field_value += 1
                    field.value = str(current_field_value)
                    hour_diff -= 1
                    tot_sum += 1
                    print(f'{proj_name=}  :  {hour_diff=}  :  {type(hour_diff)=}  :   {tot_sum=}  :  {current_field_value=}')
                    if not hour_diff:
                        break
                    if tot_sum == tot_scheduled_time:
                        break







    def _on_change_field(self, *args):
        self._update_proj_sum()
        self._update_date_sum()
        self._update_tot_sum()
        self.update()

    def _update_proj_sum(self):
        for proj, value in self._get_time_diff_for_projects().items():
            proj_sum = value['sum']
            diff = value['diff']
            self._proj_sum[proj].value = f'{proj_sum} ({diff.hours}:{str(diff.minutes).zfill(2)})'

    def _update_date_sum(self):
        date_sums = {}
        for proj in self._fields:
            for d in self._fields[proj]:
                date_sums.setdefault(d, 0)
                value_str = self._fields[proj][d].value or self._fields[proj][d].label
                if not value_str:
                    continue
                value = int(value_str)
                date_sums[d] += value
        for date, text in self._date_sum.items():
            text.value = str(date_sums[date])

    def _update_tot_sum(self):
        self._tot_sum.value = str(self._get_tot_sum())

    def _get_tot_sum(self) -> int:
        tot = 0
        for proj in self._fields:
            for d in self._fields[proj]:
                value_str = self._fields[proj][d].value or self._fields[proj][d].label
                if not value_str:
                    continue
                value = int(value_str)
                tot += value
        return tot

    def _get_time_diff_for_projects(self) -> dict[str, dict[str, utils.TimeDelta]]:
        diffs = {}
        for proj in self._fields:
            p = database.get_project(proj)
            proj_sum = 0
            for d in self._fields[proj]:
                value_str = self._fields[proj][d].value or self._fields[proj][d].label
                if not value_str:
                    continue
                value = int(value_str)
                proj_sum += value
            tot_time_in_proj = controller.get_total_time_for_project(p, time_stop=self.latest_date)
            diff = tot_time_in_proj - utils.TimeDelta(datetime.timedelta(hours=proj_sum))
            diffs[proj] = dict(
                sum=proj_sum,
                diff=diff
            )
        return diffs

    def _submit(self, *args) -> None:
        stop_date = min([self.week_dates[-1], datetime.datetime.now().date()])
        print(stop_date)
        tot_scheduled_time = controller.get_sum_of_scheduled_time(date_stop=stop_date)
        tot_submit_time = controller.get_sum_of_submitted_time(date_stop=stop_date)

        print(f'{tot_scheduled_time=}')
        print(f'{tot_submit_time=}')
        print(f'{self._tot_sum.value=}')

    def update_page(self) -> None:
        self._on_change_week()




