import datetime

import flet as ft
from time_report import database, controller
from time_report.models import TimeLog
from time_report.settings import settings


class ColorPicker(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self.controls.append(self._input_col)
        self.controls.append(ft.ElevatedButton('Flytta tid', on_click=self._submit))



