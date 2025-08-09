import sqlite3
import datetime
# Get current time to generate realistic timestamps
from zoneinfo import ZoneInfo


# STATUS_OPTIONS = ["Todo", "Done"]
# PRIORITY_OPTIONS = ["High", "Medium", "Low"]
# SOURCE_OPTIONS = ["🔒 Perso", "👩‍❤️‍👨 Famille", "👶 Yeraz", "🤱 Mama", "💼 Hameaux Légers"]
# FIRE_OPTIONS = ["🔥", "⏰", ""]


# DB COLUMNS ARE :
# ['id', 'todo_name', 'status', 'priority', 'fire_or_clock', 'source', 'deadline', 'modified_time', 'created_time', 'comments']


def init_db():
    """Initializes the DB and creates the 'todos' table if it does not exist yet"""
    with sqlite3.connect(database="todos.db") as connection:
        cursor = connection.cursor()

        query: str = '''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY,
                todo_name TEXT NOT NULL,
                status TEXT NOT NULL, 
                priority TEXT,
                fire_or_clock TEXT,
                source TEXT, 
                deadline TEXT, 
                modified_time TEXT,
                created_time TEXT, 
                comments TEXT)
        '''

        cursor.execute(query)
        connection.commit()


# Call this once at the start of  app to ensure the DB and table exist.
init_db()


def get_all_todos():
    """Retrieves all todos from the database"""
    with sqlite3.connect("todos.db") as connection:
        connection.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
        cursor = connection.cursor()

        query: str = "SELECT * FROM todos"
        cursor.execute(query)

        return cursor.fetchall()


def get_todo_by_id(todo_id: int):
    """Retrieves one todo from the database by its ID"""
    with sqlite3.connect("todos.db") as connection:
        connection.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
        cursor = connection.cursor()

        query: str = "SELECT * FROM todos WHERE id = ?"
        cursor.execute(query, (todo_id,))

        return cursor.fetchone()


def create_todo(todo_name: str, status: str, priority: str, fire_or_clock: str, source: str, deadline: str,
                modified_time: str, created_time: str, comments: str):
    """Adds a new todo inside the todos table"""
    with sqlite3.connect("todos.db") as connection:
        cursor = connection.cursor()

        query: str = "INSERT INTO todos (todo_name, status, priority, fire_or_clock, source, deadline, modified_time, created_time, comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (
        todo_name, status, priority, fire_or_clock, source, deadline, modified_time, created_time, comments))
        connection.commit()


def update_one_column(todo_id: int, column_to_update: str, new_status):
    """Update a single property for a given todo"""
    allowed_columns: list = ["todo_name", "status", "priority", "fire_or_clock", "source", "deadline", "comments"]

    if column_to_update not in allowed_columns:
        print(f"{column_to_update} is not a column of the database")
        return

    with sqlite3.connect("todos.db") as connection:
        cursor = connection.cursor()

        query: str = f"UPDATE todos SET {column_to_update} = ? WHERE id = ?"
        cursor.execute(query, (new_status, todo_id))
        connection.commit()


def delete_todo(todo_id: int):
    """Delete a specific todo"""
    with sqlite3.connect("todos.db") as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?",
                       # There is a comma at the end because the parameters of cursor.execute must be a tuple
                       # So adding a comma makes it a single element tuple
                       (todo_id,))
        connection.commit()


# 1. Get the current time in UTC (as you did)
now_utc = datetime.datetime.now(datetime.timezone.utc)
# 2. Convert it to the French timezone (Europe/Paris)
french_timezone = ZoneInfo("Europe/Paris")
now_french = now_utc.astimezone(french_timezone)
# 3. Format the result into your desired string format
NOW_FR_DATE = now_french.strftime("%d/%m/%Y")

# todo_test_1 = {
#     "todo_name": "Finalize Q3 Marketing Report",
#     "priority": "High",
#     "source": "🔒 Perso",
#     "fire_or_clock": "🔥",  # True for "fire_or_clock" (urgent)
#     "deadline": (now_french - datetime.timedelta(days=2)),
#     "status": "Done",
#     "files": '["Q3_report_final_v2.docx", "presentation_slides.pptx"]',
#     "comments": '["Approved by Jane Doe.", "Awaiting final sign-off from legal."]',
#     "created_time": (now_french - datetime.timedelta(days=10)),
#     "modified_time": (now_french - datetime.timedelta(days=2, hours=4)),
# }
#
# todo_test_2 = {
#     "todo_name": "Develop User Authentication Feature",
#     "priority": "High",
#     "source": "🔒 Perso",
#     "fire_or_clock": "🔥",
#     "deadline": (now_french - datetime.timedelta(days=5)),
#     "status": "Done",
#     "files": '"auth_module.py", "user_schema.sql"',
#     "comments": '"Deployed to production in v1.2.", "Passed all security checks."',
#     "created_time": (now_french - datetime.timedelta(days=25)),
#     "modified_time": (now_french - datetime.timedelta(days=5, hours=1)),
# }
#
# todo_test_3 = {
#     "todo_name": "Book Flights for Paris Conference",
#     "priority": "Medium",
#     "source": "👩‍❤️‍👨 Famille",
#     "fire_or_clock": "",  # False for "clock" (scheduled task)
#     "deadline": (now_french - datetime.timedelta(days=15)),
#     "status": "Todo",
#     "files": "no files",
#     "comments": "No comment",
#     "created_time": (now_french - datetime.timedelta(days=30)),
#     "modified_time": (now_french - datetime.timedelta(days=15)),
# }
#
# todo_test_4 = {
#     "todo_name": "TESTO Testo",
#     "priority": "High",
#     "source": "👩‍❤️‍👨 Famille",
#     "fire_or_clock": "⏰",  # False for "clock" (scheduled task)
#     "deadline": (now_french - datetime.timedelta(days=15)),
#     "status": "Todo",
#     "files": "no files",
#     "comments": "No commantaires",
#     "created_time": (now_french - datetime.timedelta(days=30)),
#     "modified_time": (now_french - datetime.timedelta(days=15)),
# }
#

# for todo_sample in [todo_test_1,todo_test_2,todo_test_3,todo_test_4] :
#     create_todo(todo_name=todo_sample["todo_name"], status=todo_sample["status"],
#                 source=todo_sample["source"], priority=todo_sample["priority"],
#                 fire_or_clock=todo_sample["fire_or_clock"],
#                 deadline=todo_sample["deadline"],
#                 modified_time=todo_sample["modified_time"], created_time=todo_sample["created_time"],
#                 comments=todo_sample["comments"])

# # {
# #     "todo_name": "Zizi pote",
# #     "priority": "Medium",
# #     "source": "🤱 Mama",
# #     "fire_or_clock": "⏰",  # False for "clock" (scheduled task)
# #     "deadline": (now_french - datetime.timedelta(days=15)),
# #     "status": "Todo",
# #     "files": ["flight_confirmation_AF123.pdf", "hotel_booking.pdf"],
# #     "comments": ["Got a window seat.", "Total cost was within budget."],
# #     "created_time": (now_french - datetime.timedelta(days=30)),
# #     "modified_time": (now_french - datetime.timedelta(days=15)),
# # }
# #
#
#
# # delete_todo(2)
# # update_one_column(todo_id=1, column_to_update="status", new_status="Medium")
# # delete_todo(todo_id=1)
#
