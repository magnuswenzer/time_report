import datetime

import flet as ft

from time_report import utils, controller

COLUMN_WIDTH = 200
COLUMN_WIDTH_INFO = 250


class SumTimes(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        col_sum = self._get_summarize_column()

        self.controls.append(col_sum)

    def _get_summarize_column(self) -> ft.Column:

        self._tot_worked_time = ft.Text()
        self._tot_scheduled_time = ft.Text()
        self._tot_submitted_time = ft.Text()
        self._tot_worked_minus_scheduled_time = ft.Text()
        self._tot_worked_minus_submitted_time = ft.Text()
        self._tot_scheduled_minus_submitted_time = ft.Text()

        self._tot_times_column = ft.Column([
            ft.Row([ft.Text("Total arbetad tid:", width=COLUMN_WIDTH_INFO), self._tot_worked_time]),
            ft.Row([ft.Text("Total schemalagd tid:", width=COLUMN_WIDTH_INFO), self._tot_scheduled_time]),
            ft.Row([ft.Text("Total rapporterad tid:", width=COLUMN_WIDTH_INFO), self._tot_submitted_time]),
            ft.Row([ft.Text("Arbetad minus schemalagd tid:", width=COLUMN_WIDTH_INFO), self._tot_worked_minus_scheduled_time]),
            ft.Row([ft.Text("Arbetad minus rapporterad tid:", width=COLUMN_WIDTH_INFO), self._tot_worked_minus_submitted_time]),
            ft.Row([ft.Text("Schemalagd minus rapporterad tid:", width=COLUMN_WIDTH_INFO), self._tot_scheduled_minus_submitted_time]),
        ])

        return self._tot_times_column

    def update_times(self, date: datetime.date) -> None:
        self._update_sum(date)

    def _update_sum(self, end_date: datetime.date = None) -> None:
        sum_scheduled = controller.get_sum_of_scheduled_time(date_stop=end_date)
        sum_worked = controller.get_sum_of_worked_time(date_stop=end_date)
        sum_submitted = controller.get_sum_of_submitted_time(date_stop=end_date)

        self._tot_worked_time.value = utils.get_h_str(sum_worked)
        self._tot_scheduled_time.value = utils.get_hm_str(sum_scheduled)
        self._tot_submitted_time.value = utils.get_hm_str(sum_submitted)
        self._tot_worked_minus_scheduled_time.value = utils.get_hm_str(sum_worked - sum_scheduled)
        self._tot_worked_minus_submitted_time.value = utils.get_hm_str(sum_worked - sum_submitted)
        self._tot_scheduled_minus_submitted_time.value = utils.get_hm_str(sum_scheduled - sum_submitted)
        self._tot_times_column.update()

