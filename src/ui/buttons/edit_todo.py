from nicegui import ui
from src.styles.buttons import AT_EDIT_BTN_STYLE
from typing import Callable


class EditButton:
    def __init__(self, callback_function_on_click:Callable[[],None]):
        ui.button(text="Edit", on_click=lambda: callback_function_on_click()).classes(
            AT_EDIT_BTN_STYLE).props('no-caps')


if __name__ in {"__main__", "__mp_main__"}:
    from src.models.database import TodoDatabase

    todo_num_8 = dict(TodoDatabase("../../../todos.db").get_todo_by_id(8))

    EditButton(todo_num_8).display()

    # ----APP RUNNING----
    ui.run(language='fr')
