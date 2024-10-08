import flet as ft


class PageLogTime(ft.Column):

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self._manual_project_options = []

        self._manual_row = ft.Row([
            ft.Text('Lägg till manuell tid'),
            ft.Dropdown(
                label="Projekt",
                hint_text="Vilket projekt gäller det",
                options=[
                    ft.dropdown.Option("Red"),
                    ft.dropdown.Option("Green"),
                    ft.dropdown.Option("Blue"),
                ],
                autofocus=True,
            )
        ])