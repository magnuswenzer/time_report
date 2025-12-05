import flet as ft
import winsound

from time_report import database, controller
from time_report.gui.page_day_report import PageDayReport
from time_report.gui.page_log_time import PageLogTime
from time_report.gui.page_project import PageProject
from time_report.gui.page_settings import PageSettings
from time_report.gui.page_week_report import PageWeekReport
from time_report.gui.page_week_schedule import PageWeekSchedule
from time_report.gui.page_week_submit import PageWeekSubmit
from time_report.gui.page_vab import PageVab
from time_report.gui.page_summarize import PageSummarize
from time_report.settings import settings


def _play_alert_sound():
    duration = 500  # milliseconds
    freq = 440  # Hz
    winsound.Beep(freq, duration)


class TimeReportApp(ft.Column):
    def __init__(self):
        super().__init__()
        settings.add_callback(self._on_change_settings)
        self._build()

    #     self.page = None
    #     database.create_db_and_tables()
    #     self.app = ft.app(target=self.main)
    #
    #     self.page_project.load_projects_from_database()

    def startup(self):
        self.page.overlay.append(self._dlg)
        controller.add_default_date_info()
        self.page_project.load_projects_from_database()
        self.page_log_time.update_page()

    # def main(self, page: ft.Page):
    #     self.page = page
    #     self.page.title = f'Tidrapportering ({settings.year})'
    #     self.page.window.height = 1000
    #     self.page.window.width = 1800
    #     # self.page.theme_mode = ft.ThemeMode.DARK
    #     self._build()

    def _on_change_settings(self, data: dict) -> None:
        self.page.title = f'Tidrapportering ({data["year"]})'
        self._tab_vab.visible = data.get("show_vab", False)
        self.page.update()

    def _build(self):
        self._dialog_text = ft.Text()
        self._dlg = ft.AlertDialog(
            title=self._dialog_text
        )

        self._info_text = ft.Text('Välkommen!')

        self.page_log_time = PageLogTime(self)
        self.page_project = PageProject(self)
        self.page_day_report = PageDayReport(self)
        self.page_week_report = PageWeekReport(self)
        self.page_week_schedule = PageWeekSchedule(self)
        self.page_week_submit = PageWeekSubmit(self)
        self.page_vab = PageVab(self)
        self.page_summarize = PageSummarize(self)
        self.page_settings = PageSettings(self)
        self.expand = True

        self._tab_vab = ft.Tab(
                    text="VAB",
                    icon=ft.icons.CHILD_CARE,
                    content=self.page_vab,
                )
        self._tab_vab.visible = settings.data.get("show_vab", False)

        self._tabs = ft.Tabs(
            selected_index=1,
            animation_duration=300,
            on_change=self._on_change_tab,
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
                ft.Tab(
                    text="Dagens arbete",
                    icon=ft.icons.VIEW_DAY,
                    content=self.page_day_report,
                ),
                ft.Tab(
                    text="Veckans arbete",
                    icon=ft.icons.CALENDAR_VIEW_WEEK,
                    content=self.page_week_report,
                ),
                ft.Tab(
                    text="Veckoschema",
                    icon=ft.icons.SCHEDULE,
                    content=self.page_week_schedule,
                ),
                ft.Tab(
                    text="Rapportera tid",
                    icon=ft.icons.REPORT,
                    content=self.page_week_submit,
                ),
                self._tab_vab,
                ft.Tab(
                    text="Summering",
                    icon=ft.icons.SUMMARIZE,
                    content=self.page_summarize,
                ),
                ft.Tab(
                    text="Inställningar",
                    icon=ft.icons.SETTINGS,
                    content=self.page_settings,
                ),

            ],
            expand=1, expand_loose=True
        )

        self._tabs.selected_index = 0

        self.controls.append(self._info_text)
        self.controls.append(self._tabs)

    def show_dialog(self, text: str):
        print('===========', text)
        self._dialog_text.value = text
        self._open_dlg()

    def _open_dlg(self, *args):
        self._dlg.open = True

    def show_info(self, text: str, alert: bool = False) -> None:
        if alert:
            _play_alert_sound()
        self._info_text.value = text
        self._info_text.update()

    def _on_change_tab(self, *args):
        if self._tabs.selected_index == 0:
            self.page_log_time.update_page()
        elif self._tabs.selected_index == 1:
            self.page_project.update_page()
        elif self._tabs.selected_index == 2:
            self.page_day_report.update_page()
        elif self._tabs.selected_index == 3:
            self.page_week_report.update_page()
        elif self._tabs.selected_index == 4:
            self.page_week_schedule.update_page()
        elif self._tabs.selected_index == 5:
            self.page_week_submit.update_page()
        elif self._tabs.selected_index == 6:
            self.page_vab.update_page()

    def update_pages(self) -> None:
        self.page_project.update_page()
        self.page_log_time.update_page()
        self.page_week_report.update_page()


def main(page: ft.Page):
    database.create_db_and_tables()
    page.title = f'Tidrapportering ({settings.year})'
    page.window.height = 1000
    page.window.width = 1800
    # page.title = "Arbetstid"
    # page.window.height = 900
    # page.window.width = 1700
    page.theme_mode = ft.ThemeMode.DARK
    # page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # page.scroll = ft.ScrollMode.ADAPTIVE

    # create app control and add it to the page
    app = TimeReportApp()
    page.add(app)
    app.startup()



