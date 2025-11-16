from nicegui import ui
from src.styles.buttons import AT_DELETE_BTN_STYLE
from typing import Callable


class DeleteButton:
    def __init__(self, callback_function_on_click:Callable[[],None]):
        ui.button(text="Delete", on_click=lambda: callback_function_on_click()).classes(
            AT_DELETE_BTN_STYLE).props('no-caps')


if __name__ in {"__main__", "__mp_main__"}:
   print(zizi)
