import datetime

import flet as ft
from time_report import database, controller
from time_report.gui.manual_log_time import ManualLogTime
from time_report.models import Project
from time_report.settings import settings


class LogTimeButtons(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self._buttons = {}
        self._running_proj = None
        self.expand = True

        self._current_project = ft.Text(size=40)
        self._button_column_1 = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self._button_column_2 = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self._button_column_3 = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

        self.controls.append(ft.Row([ft.Text('Nu loggas:'), self._current_project]))
        # self.controls.append(self._current_project)
        self.controls.append(ft.ElevatedButton('Stoppa', on_click=self._stop))
        self.controls.append(ft.Divider())
        self.controls.append(ft.Row([
            self._button_column_1,
            self._button_column_2,
            self._button_column_3
        ], expand=True))

    def update_frame(self) -> None:
        self._button_column_1.controls = []
        self._button_column_2.controls = []
        self._button_column_3.controls = []
        self._buttons = {}
        #running_tlog = database.get_running_time_log(year=settings.year)
        running_tlog = database.get_running_time_log()
        print(f'{running_tlog=}')
        print(f'{settings.year=}')
        self._running_proj = None
        if running_tlog and running_tlog.time_start.year == settings.year:
            self._running_proj = database.get_project(running_tlog.project_id, year=settings.year)
            self._current_project.value = self._running_proj.name
            self.main_app.show_info(
                f'Start loggning {self._running_proj.name} ({running_tlog.time_start.strftime("%H:%M")})')
            self._current_project.update()
        target_col = self._button_column_1
        for i, proj in enumerate(database.get_projects(year=settings.year)):
            btn = ft.ElevatedButton(proj.name,
                                    width=250,
                                    on_click=lambda e, p=proj: self._on_select_proj(e, p))
            if not proj.active:
                btn.disabled = True
            self._buttons[proj.name] = btn
            target_col.controls.append(btn)
            if i == 8:
                target_col = self._button_column_2
            if i == 17:
                target_col = self._button_column_3
        self.update()

    def _on_select_proj(self, e, proj: Project):
        if proj == self._running_proj:
            return
        if datetime.datetime.now().year != settings.year:
            self.main_app.show_info(f'Du kan inte loga tid för år {settings.year}')
            return
        self._running_proj = proj
        controller.start_logging(proj.name)
        self.main_app.show_info(
            f'Start loggning {proj.name} ({datetime.datetime.now().strftime("%H:%M")})')
        self._current_project.value = proj.name
        self._current_project.update()

    def _stop(self, e) -> None:
        controller.stop_logging()
        self._current_project.value = ''
        self._current_project.update()
        self._running_proj = None
        self.main_app.show_info(
            f'Loggning stoppad ({datetime.datetime.now().strftime("%H:%M")})')


