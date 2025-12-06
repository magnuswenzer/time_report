import flet as ft
from flet_contrib import color_picker
from typing import Callable


class ColorButtonTemplate(ft.Column):

    def __init__(self,
                 label: str = 'Välj färg',
                 color: str = "red",
                 callback: Callable | None = None
                 ):
        super().__init__()
        self._label = label
        self._color = color
        self._open = False
        self._callback = callback

        self._container = ft.Container(content=ft.Text(' ' * 30))
        self._btn = self._get_button()
        self._select_btns = self._get_select_buttons()
        self._picker = self._get_color_picker()
        self._select_btns.visible = False
        self._picker.visible = False

        self.controls = [
            ft.Row([self._btn, self._container]),
            self._picker,
            self._select_btns,
        ]

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, color: str) -> None:
        self._color = color
        self._container.bgcolor = self._color
        self._container.update()
        #self.close_picker()

    def open_picker(self):
        self._open = True
        #self._btn.visible = False
        self._picker.color = self._color
        self._picker.visible = True
        self._select_btns.visible = True
        self.update()

    def close_picker(self):
        self._open = False
        #self._btn.visible = True
        self._picker.visible = False
        self._select_btns.visible = False
        self.update()

    def _on_click_color_button(self, e: ft.ControlEvent):
        self.open_picker()

    def _on_ok_color(self, e: ft.ControlEvent):
        self._color = self._picker.color
        self._btn.bgcolor = self._color
        self._btn.update()
        self.close_picker()
        if self._callback:
            self._callback(self._color)

    def _on_cancel_color(self, e: ft.ControlEvent):
        self.close_picker()

    def _get_button(self) -> ft.ElevatedButton:
        btn = ft.ElevatedButton(
            text=self._label,
            icon=ft.icons.COLORIZE,
            on_click=self._on_click_color_button,
            bgcolor=self._color,
        )
        return btn

    def _get_select_buttons(self) -> ft.Row:
        ok_btn = ft.ElevatedButton(
            text='Välj',
            on_click=self._on_ok_color)

        cancel_btn = ft.ElevatedButton(
            text='Avbryt',
            on_click=self._on_cancel_color)

        return ft.Row([ok_btn, cancel_btn])

    def _get_color_picker(self) -> color_picker.ColorPicker:
        picker = color_picker.ColorPicker(
            color=self._color,
        )
        return picker

    @property
    def value(self) -> str:
        return self._color

    @value.setter
    def value(self, color: str) -> None:
        self._color = color


