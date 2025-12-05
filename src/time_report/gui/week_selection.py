import flet as ft
import datetime

from time_report import controller, utils


class WeekSelection(ft.Column):

    def __init__(self, callback_change_week):
        super().__init__()

        label_width = 300

        self._callback_change_week = callback_change_week

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

        self._tot_overtime_text = ft.Text('Total övertid just nu:', width=label_width)
        self._tot_overtime = ft.Text()

        self._work_hours_this_week = ft.Text()

        self._report_diff = ft.Text()

        self.controls = [
            ft.Text(""),
            ft.Row([
            ft.IconButton(icon=ft.icons.ARROW_LEFT, on_click=self._goto_previous_week),
            self._week_dropdown,
            ft.IconButton(icon=ft.icons.ARROW_RIGHT, on_click=self._goto_next_week),
            ft.ElevatedButton('Gå till den här veckan', on_click=self.goto_this_week),
            ft.ElevatedButton('Gå till första veckan som inte rapporterats', on_click=self._goto_first_unreported_week),
            ]),
            ft.Row([
                ft.Text('Antal arbetstimmar den här veckan', width=label_width),
                self._work_hours_this_week
            ]),
            ft.Row([
                self._tot_overtime_text,
                self._tot_overtime,
            ]),
            ft.Row([
                ft.Text('Rapporterad extratid:', width=label_width),
                self._report_diff,
            ]),
            ft.Divider(),
            ft.Text("")
        ]

    @property
    def value(self) -> str:
        return self._week_dropdown.value

    @property
    def week(self) -> int:
        return int(self.value)

    def _on_change_week(self, *args):
        week_dates = utils.get_week_dates(self.week)
        last_date = min([datetime.datetime.now().date(), week_dates[-1]])
        self._update_tot_overtime(date=last_date)
        # self._update_report_diff()
        self._update_work_hours_this_week()
        self._callback_change_week()

    def goto_this_week(self, *args):
        self._week_dropdown.value = str(int(datetime.datetime.now().strftime('%W').lstrip('0')) + 1)
        self._week_dropdown.update()
        self._on_change_week()

    def _goto_previous_week(self, *args):
        week = int(self._week_dropdown.value) - 1
        if week == 0:
            week = 1
        self._week_dropdown.value = str(week)
        self._week_dropdown.update()
        self._on_change_week()

    def _goto_next_week(self, *args):
        week = int(self._week_dropdown.value) + 1
        if week == 54:
            week = 53
        self._week_dropdown.value = str(week)
        self._week_dropdown.update()
        self._on_change_week()

    def _goto_first_unreported_week(self, *args):
        latest_sub = controller.get_latest_submitted_time()
        week_nr = '1'
        if latest_sub:
            week_nr = str(int(latest_sub.date.strftime('%W')) + 1)

        self._week_dropdown.value = week_nr
        self._week_dropdown.update()
        self._on_change_week()

    def _update_tot_overtime(self, date: datetime.date = None) -> None:
        today = datetime.datetime.now().date()
        if date:
            date = min([date, today])
        else:
            date = today
        scheduled_time = controller.get_sum_of_scheduled_time(date_stop=date)
        # scheduled_time = controller.get_sum_of_scheduled_time(date_stop=today)
        # worked_time = controller.get_sum_of_worked_time()
        worked_time = controller.get_sum_of_worked_time(date_stop=date, include_ongoing=True)
        diff = worked_time-scheduled_time

        self._tot_overtime.value = f'{diff.hours}:{str(diff.minutes).zfill(2)}          '
        self._tot_overtime.update()
        self._tot_overtime_text.value = f"Total övertid (tom. {date}): "
        self._tot_overtime_text.update()

    def _update_work_hours_this_week(self):
        percent = controller.get_work_percentage_for_week(self.week)
        tot_time: utils.TimeDelta = controller.get_sum_of_scheduled_time_for_week(self.week)
        if tot_time.minutes:
            self._work_hours_this_week.value = f'{tot_time.hours}:{str(tot_time.minutes).zfill(2)} ({percent}%)'
        else:
            self._work_hours_this_week.value = f'{tot_time.hours} ({percent}%)'
        self._work_hours_this_week.update()

    def _update_report_diff(self):
        today = datetime.datetime.now().date()
        latest_sub = controller.get_latest_submitted_time()
        worked_time = controller.get_sum_of_worked_time(date_stop=latest_sub.date)
        reported_time = controller.get_sum_of_submitted_time(date_stop=latest_sub.date)
        diff_rep = worked_time - reported_time
        self._report_diff.value = f'{diff_rep.hours}:{str(diff_rep.minutes).zfill(2)}'
        self._report_diff.update()

