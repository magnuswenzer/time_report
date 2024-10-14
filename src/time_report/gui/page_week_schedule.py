import datetime

import flet as ft
from time_report import database, controller
from time_report import utils
from time_report.gui import week_selection


class PageWeekSchedule(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self._weekday_fields = [
            ft.TextField(label='Måndag', input_filter=ft.NumbersOnlyInputFilter()),
            ft.TextField(label='Tisdag', input_filter=ft.NumbersOnlyInputFilter()),
            ft.TextField(label='Onsdag', input_filter=ft.NumbersOnlyInputFilter()),
            ft.TextField(label='Tordag', input_filter=ft.NumbersOnlyInputFilter()),
            ft.TextField(label='Fredag', input_filter=ft.NumbersOnlyInputFilter()),
            ft.TextField(label='Lördag', input_filter=ft.NumbersOnlyInputFilter()),
            ft.TextField(label='Söndag', input_filter=ft.NumbersOnlyInputFilter()),
        ]

        width = 100
        self._dates = [
            ft.Text(width=width),
            ft.Text(width=width),
            ft.Text(width=width),
            ft.Text(width=width),
            ft.Text(width=width),
            ft.Text(width=width),
            ft.Text(width=width),
        ]

        button_col = ft.Column([
            ft.ElevatedButton('Sätt den här veckan', on_click=self._apply_to_current_week, icon=ft.icons.CALENDAR_TODAY),
            ft.ElevatedButton('Sätt den här veckan och alla efter', on_click=self._apply_to_current_week_and_following),
            ft.ElevatedButton('Sätt alla veckor', on_click=self._apply_to_all_weeks),
        ])

        self.week_selection = week_selection.WeekSelection(callback_change_week=self._on_change_week)

        dates_col = ft.Column()

        for date, field in zip(self._dates, self._weekday_fields):
            dates_col.controls.append(ft.Row([
                date, field
            ]))

        self.controls = [
            self.week_selection,
            ft.Row([
                dates_col,
                button_col
            ])
        ]

    @property
    def week(self) -> int:
        return int(self.week_selection.value)

    @property
    def week_dates(self) -> list[datetime.date]:
        return utils.get_week_dates(self.week)

    def _on_change_week(self, *args):
        self._update_dates()
        self._update_date_info()

    def _update_dates(self):
        for text, date in zip(self._dates, self.week_dates):
            text.value = date.strftime(utils.DATE_FORMAT)
            text.update()

    def _update_date_info(self):
        wdates = self.week_dates
        print(f'{wdates=}')
        print(f'{self._dates=}')
        dinfos = controller.get_dates_info(wdates[0], wdates[-1])
        print(f'{dinfos=}')
        for date, field, info in zip(self._dates, self._weekday_fields, dinfos):
            field.value = ''
            date.color = 'primary'
            if info.time_in_plan:
                td = utils.TimeDelta(info.time_in_plan)
                field.value = str(td.hours)
            if info.non_working_day:
                date.color = 'red'
            field.update()
            date.update()

    def update_page(self) -> None:
        self._on_change_week()

    def _get_info_from_week(self) -> list[dict]:
        info = []
        for date_text, field in zip(self._dates, self._weekday_fields):
            day = dict(date=datetime.datetime.strptime(date_text.value, utils.DATE_FORMAT).date())
            if field.value:
                day['nr_hours'] = int(field.value)
            info.append(day)
        return info

    def _apply_to_current_week(self, *args):
        info = self._get_info_from_week()
        controller.set_info_for_dates(*info)
        self.update_page()

    def _apply_to_current_week_and_following(self, *args):
        info = self._get_info_from_week()
        controller.set_week_info_from_date(info[0]['date'], *info)
        self.update_page()

    def _apply_to_all_weeks(self, *args):
        info = self._get_info_from_week()
        controller.set_week_info_from_date(datetime.datetime(datetime.datetime.now().year, 1, 1).date(), *info)
        self.update_page()




