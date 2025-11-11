from nicegui import ui
from src.models.todo import Todo
from src.styles.constants import STATUS_COLORS, PRIORITY_COLORS


class TodoRow:
    def __init__(self, todo: Todo):
        self.todo = todo.from_obj_to_dict()

    def display(self) -> ui.row:
        with ui.row().classes('w-full p-3 items-center hover:bg-gray-50 cursor-pointer text-base'):
            # Fire prefix icon
            fire_icon_to_display: str = "" if self.todo["fire_or_clock"] == None else self.todo["fire_or_clock"]
            ui.label(text=f"{fire_icon_to_display}").classes('w-12 text-center text-xl')

            # To-do name (takes up all available space)
            ui.label(self.todo['todo_name']).classes('flex-grow')

            # Status pill
            status = self.todo["status"]
            ui.label(status).classes(
                f'w-28 text-center text-sm p-1 rounded-full {STATUS_COLORS.get(status, "bg-gray-200")}')

            # Priority pill
            priority = self.todo["priority"]
            ui.label(priority).classes(
                f'w-24 text-center text-sm p-1 rounded-full {PRIORITY_COLORS.get(priority, "bg-gray-200")}')

            # Deadline
            deadline = self.todo["deadline"]
            ui.label(deadline).classes('w-32 text-center')

        ui.separator()


class SubListMiniHeader:
    @classmethod
    def display(cls):
        # Mini header row on top of the todos inside the group
        with ui.row().classes('w-full px-2 py-0 items-center text-xs text-gray-500 font-normal'):
            # This empty label acts as a spacer to align with the to-do names, by taking all the available space
            ui.label().classes('flex-grow')
            # Add labels for each column, matching the widths of the data below
            ui.label('Status').classes('w-28 text-center')
            ui.label('Priority').classes('w-24 text-center')
            ui.label('Deadline').classes('w-32 text-center')


class ExpandableGroup:
    def __init__(self, *todos: Todo, group_name: str, is_group_expanded: bool = False):
        # Store todos as a list (mutable) since the list of todos could be sorted by user in GUI
        self.todos = list(todos)
        self.is_group_expanded = is_group_expanded
        self.group_name = group_name

    def display(self):
        with ui.expansion().props("switch-toggle-side").classes('w-full text-base') as group_header:
            # Customize visually the header of the group with add_slot
            with group_header.add_slot("header"):
                with ui.row().classes("items-center"):
                    ui.label(f'{self.group_name}').classes("bg-gray-200 rounded px-2 py-1")
                    ui.label(f'{len(self.todos)}').classes("ml-1 text-gray-500")

            # This column holds all the todos of the group
            with ui.column().classes('w-full gap-0'):
                SubListMiniHeader().display()

                for todo in self.todos:
                    todo_object = Todo.from_dict_to_obj(todo)
                    todo_row = TodoRow(todo_object)
                    todo_row.display()


##########################################
##########################################
if __name__ in {"__main__", "__mp_main__"}:
    # DUMMY DATA
    todo_sample_data_1 = {
        "id": 22,
        "todo_name": "Buy groceries",
        "status": "Todo",
        "priority": "High",
        "fire_or_clock": "🔥",
        "source": "🔒 Perso",
        "deadline": "25/12/2024",
        "modified_time": "20/12/2024 10:30",
        "created_time": "19/12/2024 09:15",
        "comments": "Don't forget the milk",
        "attachment_dir": "folder_123"
    }

    todo_sample_data_2 = {
        "id": 23,
        "todo_name": "Prepare Q4 presentation slides",
        "status": "Todo",
        "priority": "Medium",
        "fire_or_clock": "⏰",
        "source": "🔒 Perso",
        "deadline": "15/01/2025",
        "modified_time": "10/01/2025 14:20",
        "created_time": "08/01/2025 11:00",
        "comments": "Need to include new sales figures.",
        "attachment_dir": "presentations/q4_final"
    }

    todo_sample_data_3 = {
        "id": 24,
        "todo_name": "Book flight to conference",
        "status": "Done",
        "priority": "High",
        "fire_or_clock": "🔥",
        "source": "🔒 Perso",
        "deadline": "10/12/2024",
        "modified_time": "05/12/2024 09:00",
        "created_time": "01/12/2024 17:30",
        "comments": "Booked on AirFrance. Confirmation in email.",
        "attachment_dir": ""
    }

    todo_sample_data_4 = {
        "id": 25,
        "todo_name": "Call the electrician",
        "status": "Todo",
        "priority": "Low",
        "fire_or_clock": "⏰",
        "source": "🔒 Perso",
        "deadline": "30/11/2024",
        "modified_time": "25/11/2024 08:00",
        "created_time": "25/11/2024 08:00",
        "comments": "",
        "attachment_dir": "contacts/services"
    }

    # Expandable group
    ExpandableGroup(todo_sample_data_1, todo_sample_data_4, todo_sample_data_2, group_name="Source").display()

    # Transform the todo dict sample into a Todo object
    # test_todo = Todo.from_dict_to_obj(todo_sample_data_1)

    # Create the TodoRow instance from Todo object
    # test_todo_row = TodoRow(test_todo)

    # Display sub list mini header
    # SubListMiniHeader.display()

    # Display 1 todo row
    # test_todo_row.display()

    ui.run(language='fr')
