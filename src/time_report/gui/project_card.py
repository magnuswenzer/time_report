from typing import Callable

import flet as ft

from time_report import database, controller, utils
from time_report.models import Project


def get_int_or_none(value: str) -> int | None:
    if not value.strip():
        return None
    return int(value)


def get_str(value: int | None | str) -> str:
    if value is None:
        return ''
    return str(value).strip()


class ProjectCard(ft.Card):

    def __init__(self, callback_delete: Callable, project: Project = None, main_app=None):
        super().__init__()
        self.proj: Project | None = None
        self.isolated = True
        self._color = None
        self.main_app = main_app

        self._callback_delete = callback_delete

        self._time_worked = ft.Text()
        self._time_reported = ft.Text()
        self._extra_time = ft.Text()

        color = 'green'

        self._name = ft.TextField(label='Namn', color=color)
        self._hours_in_plan = ft.TextField(label='Timmar i plan', color=color)
        self._contact = ft.TextField(label='Kontaktperson', color=color)
        self._project_number = ft.TextField(label='Projektnummer', color=color)
        self._kst = ft.TextField(label='Kostnadsställe', color=color)

        row_time_worked = ft.Row([ft.Text('Arbetad tid:'), self._time_worked])
        row_time_reported = ft.Row([ft.Text('Rapporterad tid:'), self._time_reported])
        row_extra_time = ft.Row([ft.Text('Extratid:'), self._extra_time])

        self._button_color = ft.ElevatedButton('Välj färg')

        self._button_edit = ft.IconButton(icon=ft.icons.EDIT, on_click=self._set_edit_mode)
        self._button_save = ft.IconButton(icon=ft.icons.SAVE, on_click=self._save)
        self._button_abort = ft.IconButton(icon=ft.icons.CLOSE, on_click=self._abort)
        self._button_delete = ft.IconButton(icon=ft.icons.DELETE, on_click=self._delete)

        self._option_col = ft.Column([
            self._button_edit,
            self._button_save,
            self._button_abort,
            self._button_delete,
        ])

        self._fields = ft.Column([
            self._name,
            self._project_number,
            self._hours_in_plan,
            row_time_worked,
            row_time_reported,
            row_extra_time,
            self._kst,
            self._contact] )

        self.content = ft.Row([
            self._fields,
            self._option_col
        ])

        if project:
            self.set(project)
        else:
            self._set_edit_mode(update=False)

    def _abort(self, e):
        self.set(self.proj)
        self._set_view_mode()

    def _save(self, *args):
        if not self.name:
            return
        if self.proj:
            self.proj.name = self.name
            self.proj.contact = self.contact
            self.proj.project_number = self.project_number
            self.proj.kst = self.kst
            self.proj.hours_in_plan = self.hours_in_plan
        else:
            obj = Project(
                name=self.name,
                contact=self.contact,
                project_number=self.project_number,
                kst=self.kst,
                hours_in_plan=self.hours_in_plan
            )

            self.proj = obj
        database.add_object(self.proj)
        self.main_app.update_pages()
        self._set_view_mode()

    def _delete(self, *args):
        if self.proj:
            if database.get_time_logs_for_project(self.proj):
                return
        self._callback_delete(self)

    @property
    def name(self) -> str:
        return get_str(self._name.value)

    @name.setter
    def name(self, value: str):
        self._name.value = get_str(value)

    @property
    def hours_in_plan(self) -> int:
        return get_int_or_none(self._hours_in_plan.value )

    @hours_in_plan.setter
    def hours_in_plan(self, value: int):
        self._hours_in_plan.value = get_str(value)

    @property
    def contact(self) -> str:
        return get_str(self._contact.value)

    @contact.setter
    def contact(self, value: str):
        self._contact.value = get_str(value)

    @property
    def project_number(self) -> int:
        return get_int_or_none(self._project_number.value)

    @project_number.setter
    def project_number(self, value: int):
        self._project_number.value = get_str(value)

    @property
    def kst(self) -> int:
        return get_int_or_none(self._kst.value)

    @kst.setter
    def kst(self, value: int):
        self._kst.value = get_str(value)

    @property
    def time_worked(self) -> int:
        return get_int_or_none(self._time_worked.value)

    @time_worked.setter
    def time_worked(self, value: int):
        self._time_worked.value = get_str(value)

    def set_color(self, color: str):
        self._name.color = color
        self._hours_in_plan.color = color
        self._contact.color = color
        self._project_number.color = color
        self._kst.color = color

    def set(self, proj: Project) -> None:
        self.proj = proj
        self.name = proj.name
        self.project_number = proj.project_number
        self.contact = proj.contact
        self.hours_in_plan = proj.hours_in_plan
        self.kst = proj.kst
        self._color = proj.color
        self._set_view_mode(update=False)

    def _set_view_mode(self, *args, update: bool = True) -> None:
        self._fields.disabled = True
        self._button_edit.disabled = False
        self._button_save.disabled = True
        if update:
            self._fields.update()
            self._option_col.update()

    def _set_edit_mode(self, *args, update: bool = True) -> None:
        self._fields.disabled = False
        self._button_edit.disabled = True
        self._button_save.disabled = False
        if update:
            self._fields.update()
            self._option_col.update()

    def update_card(self):
        latest_date = None
        latest_sub = controller.get_latest_submitted_time()
        if latest_sub:
            latest_date = latest_sub.date
        dt_worked = controller.get_total_time_for_project(proj=self.proj, date_stop=latest_date) or utils.TimeDelta()
        dt_reported = controller.get_sum_of_submitted_time(date_stop=latest_date, proj=self.proj) or utils.TimeDelta()
        dt_extra = dt_worked - dt_reported

        self._time_worked.value = f'{dt_worked.hours}:{str(dt_worked.minutes).zfill(2)}'
        self._time_reported.value = f'{dt_reported.hours}:{str(dt_reported.minutes).zfill(2)}'
        self._extra_time.value = f'{dt_extra.hours}:{str(dt_extra.minutes).zfill(2)}'
        self.update()
