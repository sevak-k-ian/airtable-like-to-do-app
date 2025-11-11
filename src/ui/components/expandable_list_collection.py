from nicegui import ui
from src.ui.components.expandable_todo_list import ExpandableGroup

class GroupedTodoListsColumn:
    def __init__(self,*expandable_lists: ExpandableGroup, grouping_property:str):
        self.expandable_lists: list = list(expandable_lists)
        self.grouping_property : str = grouping_property

    def display(self):
        with ui.column().classes("w-full"):
            for expandable_list in self.expandable_lists:
                expandable_list.display()





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
    group_1 = ExpandableGroup(todo_sample_data_1, todo_sample_data_2, group_name="Source")
    group_2 = ExpandableGroup(todo_sample_data_3, todo_sample_data_4, group_name="Source")

    GroupedTodoListsColumn(group_1,group_2,grouping_property="source").display()

    ui.run(language='fr')
