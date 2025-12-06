import datetime

import flet as ft

from time_report import database, controller
from time_report import utils
from time_report.gui import week_selection, sum_times
from time_report.models import Project
from time_report.settings import settings
from time_report.utils import TimeDelta


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
        self._squash_times = ft.Checkbox(label='Tryck ihop', on_change=self._toggle_squash)
        self._remove_zeros_in_label = ft.Checkbox(label='Ta bort nollor', on_change=self._toggle_remove_zeros_in_label)

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
                self._squash_times,
                self._remove_zeros_in_label,
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

    def _toggle_squash(self, *args):
        if self._squash_times.value:
            self._remove_zeros_in_label.value = False
            self._remove_zeros_in_label.update()
        self._on_change_week()

    def _toggle_remove_zeros_in_label(self, *args):
        if self._remove_zeros_in_label.value:
            self._squash_times.value = False
            self._squash_times.update()
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

    def _get_total_week_td_for_submitted_or_worked(self, proj: Project) -> TimeDelta:
        week_td = controller.get_total_submitted_time_for_project_and_week(proj,
                                                                           self.week)
        if not week_td:
            week_td = controller.get_total_time_for_project_and_week(proj, self.week)
        return week_td

    def _set_default_time_in_field_labels(self):
        for proj in database.get_projects(year=settings.year):
            if proj.name not in self._fields:
                continue
            for d, date in enumerate(self._week_dates):
                label = ''
                td = controller.get_total_time_for_project_and_day(proj, date)
                if td:
                    label = str(td.hours)
                self._fields[proj.name][d].label = label
                self._fields[proj.name][d].tooltip = label

    def _set_squashed_suggestions_in_fields(self):
        percent = controller.get_work_percentage_for_week(self.week)
        # tot_time: utils.TimeDelta = controller.get_sum_of_scheduled_time_for_week(self.week)
        nr_hours_per_day = int(8 * percent / 100)

        # Get total time
        time_left_in_proj = {}
        for proj in database.get_projects(year=settings.year):
            if proj.name not in self._fields:
                continue
            total_time = controller.get_total_time_for_project_and_week(
                proj=proj,
                week_number=self.week
            )
            if not total_time:
                continue
            time_left_in_proj[proj.name] = total_time.hours


            # Set suggestions
        time_left_of_day = {}
        time_left_of_day = dict((d, nr_hours_per_day) for d in range(6))

        while sum(time_left_in_proj.values()):
            sum_before = sum(time_left_in_proj.values())
            print(f"while: {sum(time_left_in_proj.values())=}")
            proj_name, t = sorted(time_left_in_proj.items(),
                   key=lambda kv: (kv[1], kv[0]),
                   reverse=True)[0]
            print()
            print(f"{proj_name=}")
            self._set_time_for_project(
                    proj_name=proj_name,
                    value_to_set=t,
                    time_left_of_day=time_left_of_day,
                    time_left_in_proj=time_left_in_proj,
            )
            if sum(time_left_in_proj.values()) == sum_before:
                break

        self._cleanup_fields()


        # for proj in database.get_projects(year=settings.year):
        # for proj_name, t in sorted(time_left_in_proj.items(),
        #                            key=lambda kv: (kv[1], kv[0]),
        #                            reverse=True):
        #     # proj_name = proj.name
        #     if proj_name not in self._fields:
        #         continue
        #     print()
        #     print("-" * 100)
        #     print(f"{proj_name=}")
        #     for d, date in enumerate(self._week_dates):
        #         time_left_of_day.setdefault(d, nr_hours_per_day)
        #         if not time_left_of_day[d]:
        #             if self._fields[proj_name][d].label == 0:
        #                 self._fields[proj_name][d].label = None
        #             elif self._fields[proj_name][d].label:
        #                 self._fields[proj_name][d].value = "0"
        #             continue
        #         if not time_left_in_proj[proj_name]:
        #             if self._fields[proj_name][d].label == 0:
        #                 self._fields[proj_name][d].label = None
        #             elif self._fields[proj_name][d].label:
        #                 self._fields[proj_name][d].value = "0"
        #             continue
        #         value_to_set = min([
        #             time_left_of_day[d],
        #             time_left_in_proj[proj_name],
        #         ])
        #         if value_to_set:
        #             self._fields[proj_name][d].value = value_to_set
        #         print(f"{d}: {value_to_set=}")
        #         print(f"{d}: {time_left_of_day=}")
        #         print(f"{d}: {time_left_in_proj=}")
        #         print()
        #         time_left_of_day[d] -= value_to_set
        #         time_left_in_proj[proj_name] -= value_to_set

    def _set_time_for_project(self,
                              proj_name: str,
                              value_to_set: int,
                              time_left_of_day: dict[int, int],
                              time_left_in_proj: dict[str, int],
                              ):
        for d, t in time_left_of_day.items():
            # print(f"1: {t=} {value_to_set=}")
            if value_to_set <= t:
                self._fields[proj_name][d].value = value_to_set
                time_left_of_day[d] -= value_to_set
                time_left_in_proj[proj_name] -= value_to_set
                return

        for d, t in time_left_of_day.items():
            # print(f"2: {t=} {value_to_set=}")
            if not t:
                continue
            value_to_set = t
            self._fields[proj_name][d].value = value_to_set
            time_left_of_day[d] -= value_to_set
            time_left_in_proj[proj_name] -= value_to_set
            return




    def _create_fields(self, fill_hours: bool = False):
        rows = []
        self._fields: dict[str, dict[int, ft.TextField]] = {}
        self._date_sum = {}
        self._proj_sum = {}
        self._tot_sum = None

        for proj in database.get_projects(year=settings.year):
            week_td = self._get_total_week_td_for_submitted_or_worked(proj)
            if not week_td and not self._show_all_projs.value:
                continue
            self._fields[proj.name] = {}
            cells = []
            cells.append(ft.DataCell(ft.Text(proj.name)))
            for d, date in enumerate(self._week_dates):
                # label = ''
                # td = controller.get_total_time_for_project_and_day(proj, date)
                # if td:
                #     label = str(td.hours)
                field = ft.TextField(
                    on_change=self._on_change_field,
                    input_filter=ft.NumbersOnlyInputFilter()
                )
                # if fill_hours:
                #     field.label = label
                #     field.tooltip = label
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

    def _cleanup_fields(self):
        for proj_name in self._fields:
            for d in self._fields[proj_name]:
                # if proj_name == "Röda teamet":
                #     print("===")
                #     print(f"{self._fields[proj_name][d].value=}")
                #     print(f"{self._fields[proj_name][d].label=}")
                #     print("___")
                if self._fields[proj_name][d].value == "0" and self._fields[proj_name][d].label == "0":
                    self._fields[proj_name][d].value = None
                    self._fields[proj_name][d].label = None
                elif self._fields[proj_name][d].label and not self._fields[proj_name][d].value:
                    self._fields[proj_name][d].value = None
                    self._fields[proj_name][d].label = None

    def _cleanup_label_zeros_in_fields(self):
        for proj_name in self._fields:
            for d in self._fields[proj_name]:
                if self._fields[proj_name][d].label == "0" and not self._fields[proj_name][d].value:
                    self._fields[proj_name][d].value = None
                    self._fields[proj_name][d].label = None

    def _fix_field_colors(self):
        for proj_name in self._fields:
            for d in self._fields[proj_name]:
                label_color = "white"
                value_color = "white"
                wid = self._fields[proj_name][d]
                if wid.value:
                    value_color = settings.submit_number_color
                elif wid.label:
                    label_color = settings.submit_number_color
                wid.color = value_color
                wid.label_style = ft.TextStyle(color=label_color)
                # wid.update()


    def _create_table(self, fill_hours: bool = False):
        self._create_fields()
        if fill_hours:
            self._set_default_time_in_field_labels()
            if self._squash_times.value:
                self._set_squashed_suggestions_in_fields()
            elif self._remove_zeros_in_label.value:
                self._cleanup_label_zeros_in_fields()
        self._fix_field_colors()

    def _old_create_table(self, fill_hours: bool = False):
        rows = []
        self._fields: dict[str, dict[int, ft.TextField]] = {}
        self._date_sum = {}
        self._proj_sum = {}
        self._tot_sum = None

        for proj in database.get_projects(year=settings.year):
            week_td = self._get_total_week_td_for_submitted_or_worked(proj)
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




    # def _set_suggestion_in_fields(self) -> None:
    #     tot_sum = self._get_tot_sum()
    #     day_sums = {}
    #     # tot_scheduled_time = controller.get_sum_of_scheduled_time(date_start=self.week_dates[0], date_stop=self.week_dates[-1])
    #     scheduled_time = controller.get_sum_of_scheduled_time_per_day(date_start=self.week_dates[0], date_stop=self.week_dates[-1])
    #     tot_scheduled_time = scheduled_time['tot']
    #     for proj_name, value in self._get_time_diff_for_projects().items():
    #         hour_diff = value['diff'].hours
    #         if not hour_diff:
    #             continue
    #         for i, (d, field) in enumerate(self._fields[proj_name].items()):
    #             if not scheduled_time.get(i):
    #                 continue
    #             day_sums.setdefault(i, self._get_day_sum(i))
    #             if tot_sum == tot_scheduled_time:
    #                 break
    #             if scheduled_time[i] == day_sums[i]:
    #                 continue
    #             if not hour_diff:
    #                 continue
    #             current_field_value_str = field.value or field.label
    #             current_field_value = int(current_field_value_str or 0)
    #             date = self.week_dates[i]
    #             date_info = controller.get_date_info(date)
    #             max_nr_hours = utils.TimeDelta(date_info.time_in_plan).hours
    #             while current_field_value < max_nr_hours:
    #                 current_field_value += 1
    #                 field.value = str(current_field_value)
    #                 hour_diff -= 1
    #                 tot_sum += 1
    #                 day_sums[d] += 1
    #                 print(f'{proj_name=}  :  {hour_diff=}  :  {type(hour_diff)=}  :   {tot_sum=}  :  {current_field_value=}')
    #                 if not hour_diff:
    #                     break
    #                 if tot_sum == tot_scheduled_time:
    #                     break
    #                 if scheduled_time[d] == day_sums[d]:
    #                     break

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
        self._fix_field_colors()
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
                    continue
                value = int(value_str)
                proj_sum_current_week += value
            tot_time_in_proj = controller.get_total_time_for_project(p, date_stop=self.week_dates[-1]) or utils.TimeDelta()
            tot_submitted_time_in_proj = controller.get_sum_of_submitted_time(proj=p, date_stop=None)

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


    def update_page(self) -> None:
        self.week_selection.goto_active_week()
        self._on_change_week()




