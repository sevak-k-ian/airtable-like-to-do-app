from dataclasses import dataclass

@dataclass()
class Todo:
    name: str
    status: str
    last_modified: str | None = None
    created_time: str | None = None
    id: int | None = None
    priority: str | None = None
    fire: str | None = None
    source: str | None = None
    deadline: str | None = None
    comments: str | None = None
    attachments: str | None = None

    @classmethod
    def from_dict_to_obj(cls, row_dict:dict) -> "Todo":
        """Create Todo object from database row"""
        return cls(
            name = row_dict["todo_name"],
            status = row_dict["status"],
            last_modified = row_dict.get("modified_time"),
            created_time = row_dict.get("created_time"),
            id = row_dict.get("id"),
            priority = row_dict.get("priority"),
            fire = row_dict.get("fire_or_clock"),
            source = row_dict.get("source"),
            deadline = row_dict.get("deadline"),
            comments = row_dict.get("comments"),
            attachments =row_dict.get("attachment_dir")
        )

    def from_obj_to_dict(self)-> dict:
        """Create row/dict from todo object."""
        todo_as_dict = {
            "id": self.id,
            "todo_name": self.name,
            "status": self.status,
            "priority": self.priority,
            "fire_or_clock": self.fire,
            "source": self.source,
            "deadline": self.deadline,
            "modified_time": self.last_modified,
            "created_time": self.created_time,
            "comments": self.comments,
            "attachment_dir": self.attachments
        }
        return todo_as_dict





test_row = {
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

if __name__ == "__main__":
    todo = Todo.from_dict_to_obj(test_row)
    print(todo)
    dict_version = todo.from_obj_to_dict()
    print(dict_version)



