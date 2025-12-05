import datetime

import flet as ft
import winsound

from time_report import database, controller
from time_report import utils
from time_report.gui import week_selection, sum_times
from time_report.settings import settings


class PageWeekSubmit(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        label_width = 300

        self._week_dates = []

        self.week_selection = week_selection.WeekSelection(callback_change_week=self._on_change_week)

        self.sum_times = sum_times.SumTimes(self.main_app)

        self._header_texts = []
        columns = [ft.DataColumn(ft.Text("Projekt"))]
        for _ in range(7):
            text = ft.Text()
            columns.append(ft.DataColumn(text))
            self._header_texts.append(text)
        columns.append(ft.DataColumn(ft.Text("TOTALT")))

        self._table = ft.DataTable(
            columns=columns,
            # columns=[ft.Column(controls=columns, scroll=True, expand=True)],
        )
        self._update_header(update=False)
        self._button_report_time = ft.ElevatedButton('Rapportera tid', on_click=self._submit)

        self._show_all_projs = ft.Checkbox(label='Visa alla projekt', on_change=self._toggle_show_all_projs)

        self._tot_overtime_text = ft.Text('Total övertid just nu:', width=label_width)
        self._tot_overtime = ft.Text()

        self._work_hours_this_week = ft.Text()

        self._report_diff = ft.Text()

        self.controls = [
            self.week_selection,
            # ft.Row([
            #     ft.Text('Antal arbetstimmar den här veckan', width=label_width),
            #     self._work_hours_this_week
            # ]),
            # ft.Row([
            #     self._tot_overtime_text,
            #     self._tot_overtime,
            # ]),
            # ft.Row([
            #     ft.Text('Rapporterad extratid:', width=label_width),
            #     self._report_diff,
            # ]),
            ft.Row([
                self._show_all_projs,
            ]),
            # self._table,
            ft.Row([
                ft.Column(controls=[self._table], scroll=True, expand=True),
                ft.VerticalDivider(width=9, thickness=3),
                self.sum_times
            ], expand=True),
            # ft.Column(controls=[self._table], scroll=True, expand=True),
            ft.Row([
                self._button_report_time,
                # ft.ElevatedButton('Markera som rapporterad', on_click=self._mark_as_reported)
            ])
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

    def _toggle_show_all_projs(self, *args):
        self._on_change_week()

    def _on_change_week(self, *args):
        self._update_week_days()
        self._update_header()
        self._create_table(fill_hours=False)
        if not self._set_submitted_time():
            self._create_table(fill_hours=True)
            # self._set_suggestion_in_fields()
        self.update()
        # self._check_if_reported()
        self._on_change_field()
        self._update_sum_times()
        # self._update_tot_overtime()
        # last_date = min([datetime.datetime.now().date(), self._week_dates[-1]])
        # print(f"{last_date=}")
        #self._update_tot_overtime(date=last_date)
        # self._update_report_diff()
        #self._update_work_hours_this_week()
        # self.update()

    def _update_week_days(self):
        self._week_dates = utils.get_week_dates(self.week)

    def _update_header(self, update: bool = True):
        red_dates = utils.get_red_dates().get_dates(settings.year)
        for d, text, wd in zip(self._week_dates, self._header_texts, utils.WEEKDAYS):
            text.value = f'{wd}\n{d.strftime('%Y-%m-%d')}'
            text.color = None
            if d.weekday() in [5, 6] or d in red_dates:
                text.color = 'red'
            if update:
                text.update()

    def _create_table(self, fill_hours: bool = False):
        rows = []
        self._fields = {}
        self._date_sum = {}
        self._proj_sum = {}
        self._tot_sum = None

        for proj in database.get_projects(year=settings.year):
            week_td = controller.get_total_submitted_time_for_project_and_week(proj,
                                                                               self.week)
            if not week_td:
                week_td = controller.get_total_time_for_project_and_week(proj, self.week)

            if not week_td and not self._show_all_projs.value:
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
                if fill_hours:
                    field.label = label
                    field.tooltip = label
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
            text = ft.Text()
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
        day_sums = {}
        # tot_scheduled_time = controller.get_sum_of_scheduled_time(date_start=self.week_dates[0], date_stop=self.week_dates[-1])
        scheduled_time = controller.get_sum_of_scheduled_time_per_day(date_start=self.week_dates[0], date_stop=self.week_dates[-1])
        tot_scheduled_time = scheduled_time['tot']
        print(f'{tot_scheduled_time=}')
        for proj_name, value in self._get_time_diff_for_projects().items():
            hour_diff = value['diff'].hours
            if not hour_diff:
                continue
            for i, (d, field) in enumerate(self._fields[proj_name].items()):
                if not scheduled_time.get(i):
                    continue
                day_sums.setdefault(i, self._get_day_sum(i))
                if tot_sum == tot_scheduled_time:
                    break
                if scheduled_time[i] == day_sums[i]:
                    continue
                if not hour_diff:
                    continue
                current_field_value_str = field.value or field.label
                current_field_value = int(current_field_value_str or 0)
                date = self.week_dates[i]
                date_info = controller.get_date_info(date)
                max_nr_hours = utils.TimeDelta(date_info.time_in_plan).hours
                while current_field_value < max_nr_hours:
                    current_field_value += 1
                    field.value = str(current_field_value)
                    hour_diff -= 1
                    tot_sum += 1
                    day_sums[d] += 1
                    print(f'{proj_name=}  :  {hour_diff=}  :  {type(hour_diff)=}  :   {tot_sum=}  :  {current_field_value=}')
                    if not hour_diff:
                        break
                    if tot_sum == tot_scheduled_time:
                        break
                    if scheduled_time[d] == day_sums[d]:
                        break

    def _set_submitted_time(self) -> bool:
        is_submitted = False
        week_dates = self.week_dates
        self._table.disabled = False
        self._button_report_time.disabled = False
        for proj_name in self._fields:
            for i, (d, field) in enumerate(self._fields[proj_name].items()):
                date = week_dates[i]
                sub = controller.get_time_submit(proj_name, date)
                if not sub:
                    continue
                is_submitted = True
                field.value = str(utils.TimeDelta(sub.submitted_time).hours)
        if is_submitted:
            self._table.disabled = True
            self._button_report_time.disabled = True
        return is_submitted

    def _on_change_field(self, *args):
        self._update_proj_sum()
        self._update_date_sum()
        self._update_tot_sum()
        self.update()

    def _update_sum_times(self):
        self.sum_times.update_times(self._week_dates[-1])

    def _update_proj_sum(self):
        for proj, value in self._get_time_diff_for_projects().items():
            proj_sum = value['sum']
            diff = value['diff'] - utils.TimeDelta(datetime.timedelta(hours=proj_sum))
            # diff = value['diff']
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
        for d, text in self._date_sum.items():
            if d not in date_sums:
                continue
            text.value = str(date_sums[d])

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

    def _get_day_sum(self, day: int) -> int:
        tot = 0
        for proj in self._fields:
            for d in self._fields[proj]:
                if d != day:
                    continue
                value_str = self._fields[proj][d].value or self._fields[proj][d].label
                if not value_str:
                    continue
                value = int(value_str)
                tot += value
        return tot

    def _get_time_diff_for_projects(self) -> dict[str, dict[str, utils.TimeDelta | int]]:
        """
        Returns the sum of time per project and
        the difference of total time and submitted time per project
        """
        diffs = {}
        for proj in self._fields:
            p = database.get_project(proj, year=settings.year)
            proj_sum_current_week = 0
            for d in self._fields[proj]:
                value_str = self._fields[proj][d].value or self._fields[proj][d].label
                if not value_str:
                    continue
                if value_str == '0':
                    # self._fields[proj][d].value = ''
                    # self._fields[proj][d].label = ''
                    # self._fields[proj][d].update()
                    continue
                value = int(value_str)
                proj_sum_current_week += value
            tot_time_in_proj = controller.get_total_time_for_project(p, date_stop=self.week_dates[-1]) or utils.TimeDelta()
            tot_submitted_time_in_proj = controller.get_sum_of_submitted_time(proj=p, date_stop=None)

            # diff = tot_time_in_proj - tot_submitted_time_in_proj - utils.TimeDelta(datetime.timedelta(hours=proj_sum_current_week))
            diff = tot_time_in_proj - tot_submitted_time_in_proj
            diffs[proj] = dict(
                sum=proj_sum_current_week,
                diff=diff
            )
        return diffs

    def _submit(self, *args) -> None:
        try:
            for proj, proj_fields in self._fields.items():
                for i, (d, field) in enumerate(proj_fields.items()):
                    value = field.value or field.label
                    if not value:
                        continue
                    if value == '0':
                        continue
                    date = self.week_dates[i]
                    controller.submit_time(proj_name=proj, date=date, nr_hours=int(value))
            self._on_change_week() #TODO: Ändrade denna om det skulle vara strul
        except Exception as e:
            self.main_app.show_info(e, alert=True)

    def old_mark_as_reported(self, *args) -> None:
        try:
            for proj, proj_fields in self._fields.items():
                for i, (d, field) in enumerate(proj_fields.items()):
                    value = field.value or field.label
                    if not value:
                        continue
                    date = self.week_dates[i]
                    controller.mark_as_reported(proj_name=proj, date=date)
            self._check_if_reported()
        except Exception as e:
            self.main_app.show_info(e, alert=True)

    # def _update_tot_overtime(self, date: datetime.date = None) -> None:
    #     today = datetime.datetime.now().date()
    #     if date:
    #         date = min([date, today])
    #     else:
    #         date = today
    #     scheduled_time = controller.get_sum_of_scheduled_time(date_stop=date)
    #     # scheduled_time = controller.get_sum_of_scheduled_time(date_stop=today)
    #     # worked_time = controller.get_sum_of_worked_time()
    #     worked_time = controller.get_sum_of_worked_time(date_stop=date)
    #     diff = worked_time-scheduled_time
    #
    #     self._tot_overtime.value = f'{diff.hours}:{str(diff.minutes).zfill(2)}          '
    #     self._tot_overtime.update()
    #     self._tot_overtime_text.value = f"Total övertid (tom. {date}): "
    #     self._tot_overtime_text.update()
    #
    # def _update_work_hours_this_week(self):
    #     percent = controller.get_work_percentage_for_week(self.week)
    #     tot_time: utils.TimeDelta = controller.get_sum_of_scheduled_time_for_week(self.week)
    #     if tot_time.minutes:
    #         self._work_hours_this_week.value = f'{tot_time.hours}:{str(tot_time.minutes).zfill(2)} ({percent}%)'
    #     else:
    #         self._work_hours_this_week.value = f'{tot_time.hours} ({percent}%)'
    #     self._work_hours_this_week.update()
    #
    # def _update_report_diff(self):
    #     today = datetime.datetime.now().date()
    #     latest_sub = controller.get_latest_submitted_time()
    #     worked_time = controller.get_sum_of_worked_time(date_stop=latest_sub.date)
    #     reported_time = controller.get_sum_of_submitted_time(date_stop=latest_sub.date)
    #     diff_rep = worked_time - reported_time
    #     self._report_diff.value = f'{diff_rep.hours}:{str(diff_rep.minutes).zfill(2)}'
    #     self._report_diff.update()

    def update_page(self) -> None:
        self.week_selection.goto_active_week()
        self._on_change_week()




