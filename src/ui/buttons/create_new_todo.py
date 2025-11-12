from nicegui import ui


class CreateNewTodoButton:
    @staticmethod
    def display() -> None:
        new_todo_button = ui.button('Create new todo').classes(
            "bg-black rounded text-white font-semibold px-6 py-4 text-lg").props("no-caps")

if __name__ in {"__main__", "__mp_main__"}:
    CreateNewTodoButton().display()
    ui.run(language='fr')
