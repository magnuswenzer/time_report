import datetime

import flet as ft
from time_report import database, controller
from time_report import utils
from time_report.gui import week_selection


class VabPost(ft.Row):
    def __init__(self, tlog):
        super().__init__()

        self._tlog = tlog
        wd = str(utils.weekday_mapping[tlog.time_start.weekday()])
        dstring = str(tlog.time_start)[:10]
        time = f'{tlog.nr_hours}:{str(tlog.nr_minutes).zfill(2)}'
        self.controls.append(ft.Text(wd, width=150))
        self.controls.append(ft.Text(dstring, width=150))
        self.controls.append(ft.Text(time, width=150))

        self._comment = ft.Text(width=150)
        self._comment.value = tlog.comment
        self._state = ft.Checkbox('Rapporterat', on_change=self._on_change_state)
        self._set_state()

        self.controls.append(self._comment)
        self.controls.append(self._state)

    def _on_change_state(self, *args):
        if self._state.value:
            self.set_closed()
        else:
            self.set_open()

    def _set_state(self):
        state = False
        comment = self._tlog.comment
        if comment.startswith(self.done_tag):
            state = True
        self._state.value = state

    @property
    def done_tag(self) -> str:
        return 'FK'

    def set_open(self):
        comment = self._comment.value
        if comment.startswith(self.done_tag):
            comment = comment.split(':')[1].strip()
        self._comment.value = comment
        self._comment.update()

    def set_closed(self):
        comment = self._comment.value
        if not comment.startswith(self.done_tag):
            comment = ': '.join([self.done_tag, comment])
        self._comment.value = comment
        self._comment.update()

    def save(self):
        controller.update_comment_in_time_log(self._tlog.id, self._comment.value)


class PageVab(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.expand = True

        self._posts = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)

        option_row = ft.Row([
            ft.ElevatedButton('Spara', on_click=self._save_posts),
            ft.ElevatedButton('Ladda om', on_click=self.update_page),
        ])

        self.controls = [
            option_row,
            self._posts,
            ]

    def update_page(self, *args) -> None:
        self._posts.controls = []
        for tlog in controller.get_all_vab_time_logs():
            self._posts.controls.append(VabPost(tlog))
        self._posts.update()

    def _save_posts(self, *args):
        for post in self._posts.controls:
            post.save()






