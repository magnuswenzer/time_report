import datetime

import flet as ft
from time_report import database, controller
from time_report.models import TimeLog
from time_report.settings import settings


class MoveTime(ft.Row):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self._input_col = ft.Column()

        self._project_from_dropdown = ft.Dropdown(
            label="Från projekt",
            hint_text="Flytta från project",
            autofocus=False,
        )

        self._project_to_dropdown = ft.Dropdown(
            label="Till projekt",
            hint_text="Flytta till project",
            autofocus=False,
        )

        self._date_picker = ft.DatePicker(
            first_date=datetime.datetime(year=settings.year, month=1, day=1),
            last_date=datetime.datetime.now(),
            #last_date=datetime.datetime(year=datetime.datetime.now().year, month=12, day=31),
            on_change=self._on_change_manual_date,
            confirm_text='Välj',
            cancel_text='Avbryt',
            help_text='Välj datum'
                        # on_dismiss=self._on_discard_manual_date,
                    )

        # self._nr_minutes = ft.TextField(label='Antal minuter', input_filter=ft.NumbersOnlyInputFilter())
        self._nr_hours = ft.TextField(label='Antal timmar', input_filter=ft.InputFilter(regex_string=r"^[0-9]*$", allow=True, replacement_string=""))
        self._nr_minutes = ft.TextField(label='Antal minuter', input_filter=ft.InputFilter(regex_string=r"^[0-9]*$", allow=True, replacement_string=""))
        self._comment = ft.TextField(label='Kommentar')

        self._btn_pick_date = ft.ElevatedButton(
                datetime.datetime.now().strftime('%Y-%m-%d'),
                icon=ft.icons.CALENDAR_MONTH,
                on_click=lambda e: self.page.open(self._date_picker),
            )

        self._input_col.controls = [
            ft.Text('Flytta tid'),
            ft.Row([
                self._project_from_dropdown,
                ft.Text("->", size=20),
                self._project_to_dropdown,
            ]),
            self._btn_pick_date,
            ft.Row([
                self._nr_hours,
                self._nr_minutes
            ]),
            self._comment,
        ]
        self._update_project_dropdown(update=False)

        self.controls.append(self._input_col)
        self.controls.append(ft.ElevatedButton('Flytta tid', on_click=self._submit))

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.strptime(self._btn_pick_date.text, '%Y-%m-%d')

    def _update_project_dropdown(self, update: bool = True) -> None:
        options_from = []
        options_to = []
        for proj in database.get_projects(year=settings.year):
            options_from.append(ft.dropdown.Option(proj.name))
            options_to.append(ft.dropdown.Option(proj.name))
        self._project_from_dropdown.options = options_from
        self._project_to_dropdown.options = options_to
        if update:
            self._project_from_dropdown.update()
            self._project_to_dropdown.update()

    def _on_change_manual_date(self, e):
        self._btn_pick_date.text = e.control.value.strftime('%Y-%m-%d')
        self._btn_pick_date.update()

    def _submit(self, e) -> None:
        from_proj = database.get_project(self._project_from_dropdown.value, year=settings.year)
        to_proj = database.get_project(self._project_to_dropdown.value, year=settings.year)
        if not from_proj:
            self.main_app.show_info("Inget projekt valt att flytta från!")
            return
        if not to_proj:
            self.main_app.show_info("Inget projekt valt att flytta till!")
            return
        if self._project_from_dropdown.value == self._project_to_dropdown.value:
            self.main_app.show_info("Du kan inte flytta tid till samma project!")
            return
        if not any([self._nr_hours.value, self._nr_minutes.value]) or self._nr_hours.value == '-' or self._nr_minutes.value == '-':
            self.main_app.show_info('Felaktig tid angiven!')
            return

        self.main_app.show_info(f'Flyttar {self._nr_hours.value or "0"}:{self._nr_minutes.value or "0"} från {from_proj.name} till {to_proj.name}')

        nr_minutes = 0
        if self._nr_hours.value:
            nr_minutes = nr_minutes + int(self._nr_hours.value) * 60
        if self._nr_minutes.value:
            nr_minutes = nr_minutes + int(self._nr_minutes.value)

        controller.add_manual_time_to_project(from_proj, self.datetime, -nr_minutes, comment=self._comment.value)
        controller.add_manual_time_to_project(to_proj, self.datetime, nr_minutes, comment=self._comment.value)

        self._nr_hours.value = ''
        self._nr_hours.update()

        self._nr_minutes.value = ''
        self._nr_minutes.update()

        self._comment.value = ''
        self._comment.update()

    def update_frame(self) -> None:
        self._update_project_dropdown()


