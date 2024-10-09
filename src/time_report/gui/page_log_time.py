import datetime

import flet as ft
from time_report import database
from time_report.gui.manual_log_time import ManualLogTime


class PageLogTime(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self._manual_log_time = ManualLogTime(main_app)
        self.controls.append(self._manual_log_time)
        self.controls.append(ft.Divider())
        self.controls.append(ft.Divider())

    def update_page(self) -> None:
        self._manual_log_time.update_frame()

