import datetime

import flet as ft
from time_report import database, controller
from time_report.gui.manual_log_time import ManualLogTime
from time_report.models import Project


class LogTimeButtons(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self._buttons = {}
        self._running_proj = None

        self._current_project = ft.Text(size=30)
        self._button_column = ft.Column()

        self.controls.append(ft.Row([ft.Text('Nu loggas:'), self._current_project]))
        # self.controls.append(self._current_project)
        self.controls.append(ft.ElevatedButton('Stoppa', on_click=self._stop))
        self.controls.append(ft.Divider())
        self.controls.append(self._button_column)

    def update_frame(self) -> None:
        self._button_column.controls = []
        self._buttons = {}
        running_tlog = database.get_running_time_log()
        self._running_proj = None
        if running_tlog:
            self._running_proj = database.get_project(running_tlog.project_id)
            self._current_project.value = self._running_proj.name
            self._current_project.update()
        for proj in database.get_projects():
            btn = ft.ElevatedButton(proj.name,
                                  on_click=lambda e, p=proj: self._on_select_proj(e, p))
            self._buttons[proj.name] = btn
            self._button_column.controls.append(btn)
        self.update()

    def _on_select_proj(self, e, proj: Project):
        if proj == self._running_proj:
            return
        self._running_proj = proj
        controller.start_logging(proj.name)
        self._current_project.value = proj.name
        self._current_project.update()

    def _stop(self, e) -> None:
        controller.stop_logging()
        self._current_project.value = ''
        self._current_project.update()

