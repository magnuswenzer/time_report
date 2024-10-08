import os
import pathlib
import shutil
import time

import flet as ft

from time_report.gui.page_project import PageProject
from time_report.models import Project
from time_report import database


class TimeReportApp(ft.Column):
    def __init__(self):
        super().__init__()
        self._build()
    #     self.page = None
    #     database.create_db_and_tables()
    #     self.app = ft.app(target=self.main)
    #
    #     self.page_project.load_projects_from_database()

    def startup(self):
        self.page_project.load_projects_from_database()

    def main(self, page: ft.Page):
        self.page = page
        self.page.title = 'Tidrapportering'
        self.page.window.height = 1000
        self.page.window.width = 1200
        # self.page.theme_mode = ft.ThemeMode.DARK
        self._build()

    def _build(self):
        self._dialog_text = ft.Text()
        self._dlg = ft.AlertDialog(
            title=self._dialog_text
        )

        self._info_text = ft.Text(bgcolor='gray')

        self.page_log_time = PageLogTime(self)
        self.page_project = PageProject(self)

        self._tabs = ft.Tabs(
            selected_index=1,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Logga tid",
                    icon=ft.icons.LOCK_CLOCK,
                    content=self.page_log_time,
                ),
                ft.Tab(
                    text="Projekt",
                    icon=ft.icons.NOTE,
                    content=self.page_project,
                ),
            ],
            expand=1, expand_loose=True
        )

        self._tabs.selected_index = 1

        self.controls.append(self._tabs)

    def show_dialog(self, text: str):
        self._dialog_text.value = text
        self._open_dlg()

    def _open_dlg(self, *args):
        self.page.dialog = self._dlg
        self._dlg.open = True


def main(page: ft.Page):
    database.create_db_and_tables()
    page.title = "Arbetstid"
    page.window.height = 1000
    page.window.width = 1200
    page.theme_mode = ft.ThemeMode.DARK
    # page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # page.scroll = ft.ScrollMode.ADAPTIVE

    # create app control and add it to the page
    app = TimeReportApp()
    page.add(app)
    app.startup()



