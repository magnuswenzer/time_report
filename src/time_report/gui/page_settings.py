import datetime

import flet as ft
from time_report import database, controller
from time_report import utils
from time_report.settings import settings


class PageSettings(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.expand = True

        self._visible_col: ft.Column = ft.Column()
        self._visible_wids = dict()
        self._year = ft.Dropdown(label='Arbeta med år', on_change=self._on_select_year)

        self.controls = [
            ft.Divider(),
            self._year,
            self._get_visible_col()
            ]
        self._get_non_working_days_col()
        self._update_year_list(update=False)
        self._update_visible(update=False)

    def _get_visible_col(self) -> ft.Column:
        self._visible_wids['show_vab'] = ft.Switch("Visa VAB") #, on_change=self._on_change_visible)
        self._visible_col = ft.Column([
            ft.Text('Vad vill du visa'),
            self._visible_wids['show_vab'],
            ft.ElevatedButton("Uppdatera", on_click=self._on_update_visible)
        ])
        return self._visible_col

    def _get_non_working_days_col(self) -> ft.Column:
        all_date_info = controller.get_dates_info(
            date_start=datetime.date(settings.year, 1, 1),
            date_stop=datetime.date(settings.year, 12, 31),
        )
        col = ft.Column()
        col.controls.append(ft.Text("Lediga dagar"))
        controller.update_red_dates()
        # for date_info in all_date_info:
        #     if date_info.non_working_day:
        #         print(f"{date_info.date=}: {date_info.comment}")
        return col

    def update_page(self, *args) -> None:
        pass

    def _update_year_list(self, update: bool = True):
        options = []
        for year in settings.get_year_list():
            options.append(ft.dropdown.Option(str(year)))
        self._year.options = options
        self._year.value = str(settings.year)
        if update:
            self._year.update()

    def _update_visible(self, update: bool = True):
        data = settings.data
        for key, wid in self._visible_wids.items():
            save_value = data.get(key)
            print(key, save_value)
            if save_value is None:
                continue
            wid.value = save_value
        if update:
            self._visible_col.update()

    def _on_select_year(self, e):
        settings.year = int(self._year.value)

    def _on_update_visible(self, e):
        for key, wid in self._visible_wids.items():
            settings[key] = wid.value
        settings.save_settings()




