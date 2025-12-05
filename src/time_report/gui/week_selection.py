import flet as ft
import datetime

import isoweek

from time_report import controller, utils
from time_report.settings import settings


class WeekSelection(ft.Column):

    def __init__(self, callback_change_week):
        super().__init__()

        label_width = 300

        self._callback_change_week = callback_change_week

        settings.add_callback(self._callback_change_year)

        options = []

        self._week_dropdown = ft.Dropdown(
            label="Vecka",
            hint_text="Välj en vecka",
            autofocus=False,
            on_change=self._on_change_week,
            options=options,
        )
        print(f"{self._week_dropdown.bgcolor=}")
        self._update_week_list(update=False)

        self._week_dropdown.value = datetime.datetime.now().strftime('%W')

        self._tot_overtime_text = ft.Text('Total övertid just nu:', width=label_width)
        self._tot_overtime = ft.Text()

        self._work_hours_this_week = ft.Text()

        self._worked_minus_reported = ft.Text()

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
                ft.Text('Arbetad minus rapporterad:', width=label_width),
                self._worked_minus_reported,
            ]),
            ft.Divider(),
            ft.Text("")
        ]

    def _update_week_list(self, update: bool = True):
        options = []
        self._week_numbers = []
        for week in settings.weeks_of_year:
            options.append(ft.dropdown.Option(str(week.week)))
            self._week_numbers.append(week.week)
        self._week_dropdown.options = options
        if update:
            self._week_dropdown.update()

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
        self._update_report_diff(last_date)
        self._update_work_hours_this_week()
        self._save_active_week()
        if self.week == isoweek.Week.thisweek().week:
            self._week_dropdown.bgcolor = None
        else:
            self._week_dropdown.bgcolor = settings.not_current_week_alert_bgcolor
        self._week_dropdown.update()
        self._callback_change_week()

    def _callback_change_year(self, data: dict) -> None:
        self._update_week_list()

    def _save_active_week(self):
        settings.week = self.week

    def goto_this_week(self, *args):
        self.goto_week(isoweek.Week.thisweek())

    def goto_active_week(self):
        self.goto_week(settings.week)

    def goto_week(self, week: int | str | isoweek.Week):
        if not isinstance(week, isoweek.Week):
            week = isoweek.Week(settings.year, int(week))
        self._week_dropdown.value = str(week.week)
        self._week_dropdown.update()
        self._on_change_week()

    def _goto_previous_week(self, *args):
        # week = int(self._week_dropdown.value) - 1
        # if week == 0:
        #     week = 1
        week = int(self._week_dropdown.value)
        if week == self._week_numbers[0]:
            return
        self._week_dropdown.value = str(week - 1)
        self._week_dropdown.update()
        self._on_change_week()

    def _goto_next_week(self, *args):
        # week = int(self._week_dropdown.value) + 1
        # if week == 54:
        #     week = 53
        week = int(self._week_dropdown.value)
        if week == self._week_numbers[-1]:
            return
        self._week_dropdown.value = str(week + 1)
        self._week_dropdown.update()
        self._on_change_week()

    def _goto_first_unreported_week(self, *args):
        latest_sub = controller.get_latest_submitted_time()
        week_nr = '1'
        if latest_sub:
            week_nr = str(latest_sub.week.week + 1)

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
        print(f"{worked_time=}")
        print(f"{scheduled_time=}")
        print(f"{diff=}")

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

    def _update_report_diff(self, date_stop: datetime.date):
        today = datetime.datetime.now().date()
        latest_sub = controller.get_latest_submitted_time()
        if not latest_sub:
            return
        tot_scheduled_time = controller.get_sum_of_scheduled_time(date_stop=date_stop)
        # worked_time = controller.get_sum_of_worked_time(date_stop=latest_sub.date)
        worked_time = controller.get_sum_of_worked_time(date_stop=date_stop)
        # reported_time = controller.get_sum_of_submitted_time(date_stop=latest_sub.date)
        reported_time = controller.get_sum_of_submitted_time(date_stop=date_stop)

        if (date_stop > today) and (date_stop > latest_sub.date):

            date_from = latest_sub.date + datetime.timedelta(days=1)
            scheduled_time = controller.get_sum_of_scheduled_time(date_start=date_from,
                                                                  date_stop=date_stop)
            print("JAPP")

            print(f"{date_stop=}")
            print(f"{latest_sub.date=}")
            print(f"{reported_time=}")
            print(f"{worked_time - reported_time=}")
            reported_time = reported_time + scheduled_time
            print()
            print(f"{reported_time=}")
            print(f"{worked_time - reported_time=}")

        diff_rep = worked_time - reported_time
        self._worked_minus_reported.value = f'{diff_rep.hours}:{str(diff_rep.minutes).zfill(2)} (tom {date_stop})'
        self._worked_minus_reported.update()

