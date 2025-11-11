from collections import defaultdict
from typing import Any
from pprint import pprint
VALID_GROUPING_PROPERTIES = {"source", "status", "priority", "fire_or_clock"}

def group_todos_by_property(todos: list[dict[str, Any]], grouping_property: str = "source") -> dict[list[dict[str, Any]]]:
    grouped = defaultdict(list)
    for todo in todos:
        grouped[todo[f"{grouping_property}"]].append(todo)
    pprint(grouped)
    return grouped


if __name__ == "__main__":
    from src.models.database import TodoDatabase

    SAMPLE_TODOS = [
        {
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
        },
        {
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
        },
        {
            "id": 24,
            "todo_name": "Book flight to conference",
            "status": "Done",
            "priority": "High",
            "fire_or_clock": "🔥",
            "source": "👶 Yeraz",
            "deadline": "10/12/2024",
            "modified_time": "05/12/2024 09:00",
            "created_time": "01/12/2024 17:30",
            "comments": "Booked on AirFrance. Confirmation in email.",
            "attachment_dir": ""
        },
        {
            "id": 25,
            "todo_name": "Call the electrician",
            "status": "Todo",
            "priority": "Low",
            "fire_or_clock": "⏰",
            "source": "👩‍❤️‍👨 Famille",
            "deadline": "30/11/2024",
            "modified_time": "25/11/2024 08:00",
            "created_time": "25/11/2024 08:00",
            "comments": "",
            "attachment_dir": "contacts/services"
        }
    ]

if __name__ == "__main__":
    all_db_todos: list = TodoDatabase().get_list_all_todos()
    group_todos_by_property(all_db_todos, "source")
    print("zozo")