import datetime

import flet as ft
from time_report import database, controller
from time_report import utils
from time_report.gui import week_selection
from time_report.settings import settings

COLUMN_WIDTH = 200


class WeekPost(ft.Row):
    def __init__(self, w: int):
        super().__init__()
        self.active = False
        self.w = w
        self.start, self.stop = utils.get_week_range(w)

        self.worked_time = controller.get_total_time_for_week(w) or utils.TimeDelta()
        self.submitted_time = controller.get_sum_of_submitted_time(date_start=self.start, date_stop=self.stop) or utils.TimeDelta()
        self.scheduled_time = controller.get_sum_of_scheduled_time(date_start=self.start, date_stop=self.stop) or utils.TimeDelta()
        self.worked_minus_scheduled = utils.TimeDelta()
        self.worked_minus_submitted = utils.TimeDelta()
        self.submitted_minus_scheduled = utils.TimeDelta()

        print(f'{self.worked_time=}')
        print(f'{utils.TimeDelta()=}')
        print(f'{self.worked_time != utils.TimeDelta()=}')

        self.active = self.submitted_time != utils.TimeDelta()

        if self.active:
            self.worked_minus_scheduled = self.worked_time - self.scheduled_time
            self.worked_minus_submitted = self.worked_time - self.submitted_time
            self.submitted_minus_scheduled = self.submitted_time - self.scheduled_time
            self._build()

    def _build(self):
        w_str = f'{self.w} ({self.start}-{self.stop})'
        self.controls.append(ft.Text(str(w_str), width=COLUMN_WIDTH))
        self.controls.append(ft.Text(str(self.worked_time), width=COLUMN_WIDTH))
        self.controls.append(ft.Text(str(self.submitted_time), width=COLUMN_WIDTH))
        self.controls.append(ft.Text(str(self.scheduled_time), width=COLUMN_WIDTH))
        self.controls.append(ft.Text(str(self.worked_minus_scheduled), width=COLUMN_WIDTH))
        self.controls.append(ft.Text(str(self.worked_minus_submitted), width=COLUMN_WIDTH))
        self.controls.append(ft.Text(str(self.submitted_minus_scheduled), width=COLUMN_WIDTH))


class PageSummarize(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.expand = True

        self._posts = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)

        option_row = ft.Row([
            ft.ElevatedButton('Ladda om', on_click=self.update_page),
        ])

        header_row = ft.Row([
            ft.Text('Vecka', width=COLUMN_WIDTH),
            ft.Text('Arbetad tid', width=COLUMN_WIDTH),
            ft.Text('Rapporterad tid', width=COLUMN_WIDTH),
            ft.Text('Planerad tid', width=COLUMN_WIDTH),
            ft.Text('Arbetad minus planerad', width=COLUMN_WIDTH),
            ft.Text('Arbetad minus rapporterad', width=COLUMN_WIDTH),
            ft.Text('Rapporterad minus planerad', width=COLUMN_WIDTH),
        ])

        self._sum_row = ft.Row()

        self.controls = [
            option_row,
            ft.Divider(),
            header_row,
            ft.Divider(),
            self._posts,
            ft.Divider(),
            self._sum_row,
            ]

    def update_page(self, *args) -> None:
        self._posts.controls = []
        self._sum_row.controls = []
        tot_worked = utils.TimeDelta()
        tot_submitted = utils.TimeDelta()
        tot_scheduled = utils.TimeDelta()
        tot_worked_minus_scheduled = utils.TimeDelta()
        tot_worked_minus_submitted = utils.TimeDelta()
        tot_submitted_minus_scheduled = utils.TimeDelta()
        for week in utils.get_weeks_for_year(settings.year):
            w = week.week
            wp = WeekPost(w)
            if not wp.active:
                continue
            tot_worked += wp.worked_time
            tot_submitted += wp.submitted_time
            tot_scheduled += wp.scheduled_time
            tot_worked_minus_scheduled += wp.worked_minus_scheduled
            tot_worked_minus_submitted += wp.worked_minus_submitted
            tot_submitted_minus_scheduled += wp.submitted_minus_scheduled
            self._posts.controls.append(wp)
        self._posts.update()

        self._sum_row.controls.append(ft.Text(str(''), width=COLUMN_WIDTH))
        self._sum_row.controls.append(ft.Text(str(tot_worked), width=COLUMN_WIDTH))
        self._sum_row.controls.append(ft.Text(str(tot_submitted), width=COLUMN_WIDTH))
        self._sum_row.controls.append(ft.Text(str(tot_scheduled), width=COLUMN_WIDTH))
        self._sum_row.controls.append(ft.Text(str(tot_worked_minus_scheduled), width=COLUMN_WIDTH))
        self._sum_row.controls.append(ft.Text(str(tot_worked_minus_submitted), width=COLUMN_WIDTH))
        self._sum_row.controls.append(ft.Text(str(tot_submitted_minus_scheduled), width=COLUMN_WIDTH))
        self._sum_row.update()








