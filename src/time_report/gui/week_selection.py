import flet as ft
import datetime

from time_report import controller


class WeekSelection(ft.Row):

    def __init__(self, callback_change_week):
        super().__init__()

        self._callback_change_week = callback_change_week

        options = []
        for w in range(1, 54):
            options.append(ft.dropdown.Option(str(w)))

        self._week_dropdown = ft.Dropdown(
            label="Vecka",
            hint_text="Välj en vecka",
            autofocus=False,
            on_change=self._on_change_week,
            options=options
        )

        self._week_dropdown.value = datetime.datetime.now().strftime('%W')

        self.controls = [
            self._week_dropdown,
            ft.ElevatedButton('Gå till den här veckan', on_click=self._goto_this_week),
            ft.ElevatedButton('Gå till första veckan som inte rapporterats', on_click=self._goto_first_unreported_week),
        ]

    @property
    def value(self) -> str:
        return self._week_dropdown.value

    def _on_change_week(self, *args):
        self._callback_change_week()

    def _goto_this_week(self, *args):
        self._week_dropdown.value = datetime.datetime.now().strftime('%W')
        self._week_dropdown.update()
        self._on_change_week()

    def _goto_first_unreported_week(self, *args):
        # latest_sub = controller.get_latest_submitted_time()
        # week_nr = '1'
        # if latest_sub:
        #     week_nr = str(int(latest_sub.date.strftime('%W')) + 1)

        week_nr = '41'
        self._week_dropdown.value = week_nr
        self._week_dropdown.update()
        self._on_change_week()

