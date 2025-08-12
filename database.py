import sqlite3
import datetime
# Get current time to generate realistic timestamps
from zoneinfo import ZoneInfo


# STATUS_OPTIONS = ["Todo", "Done"]
# PRIORITY_OPTIONS = ["High", "Medium", "Low"]
# SOURCE_OPTIONS = ["🔒 Perso", "👩‍❤️‍👨 Famille", "👶 Yeraz", "🤱 Mama", "💼 Hameaux Légers"]
# FIRE_OPTIONS = ["🔥", "⏰", ""]


# DB 10 COLUMNS ARE :
# ['id', 'todo_name', 'status', 'priority', 'fire_or_clock', 'source', 'deadline', 'modified_time', 'created_time', 'comments', 'files']


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


def update_todo_entirely(todo_id: int, todo_name: str, status: str, priority: str, fire_or_clock: str, source: str,
                         deadline: str,
                         modified_time: str, created_time: str, comments: str):
    """
        Updates an entire to-do record in the database based on its ID.
        Note: created_time is passed but not used, as it should not be changed.
        """
    with sqlite3.connect("todos.db") as connection:
        cursor = connection.cursor()

        # The SQL query to update all relevant columns for a specific to-do.
        query = """
                UPDATE todos SET
                    todo_name = ?,
                    status = ?,
                    priority = ?,
                    fire_or_clock = ?,
                    source = ?,
                    deadline = ?,
                    comments = ?,
                    modified_time = ?
                WHERE
                    id = ?
            """

        # The tuple of values to substitute into the query's '?' placeholders.
        # The order must exactly match the order of the '?' in the query.
        values_tuple = (
            todo_name,
            status,
            priority,
            fire_or_clock,
            source,
            deadline,
            comments,
            modified_time,
            todo_id  # This corresponds to the final '?' in the WHERE clause.
        )

        cursor.execute(query, values_tuple)
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

todo_test = {
    "todo_name": "Changement de tous les éléments",
    "priority": "Medium",
    "source": "🤱 Mama",
    "fire_or_clock": "⏰",  # False for "clock" (scheduled task)
    "deadline": (now_french - datetime.timedelta(days=15)),
    "status": "Done",
    "files": "no files",
    "comments": "Yazooo",
    "created_time": (now_french - datetime.timedelta(days=30)),
    "modified_time": (now_french - datetime.timedelta(days=15))
}