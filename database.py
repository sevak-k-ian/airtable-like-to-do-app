import sqlite3
import datetime


def init_db():
    """Initializes the DB and creates the 'todos' table if it does not exist yetx"""
    with sqlite3.connect(database="todos.db") as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT NOT NULL, 
                priority TEXT,
                fire TEXT,
                source TEXT, 
                deadline DATE, 
                last_modified DATE,
                created DATE 
                comments TEXT            )
        ''')
        connection.commit()


# Call this once at the start of  app to ensure the DB and table exist.
init_db()


def create_todo(name: str, status: str, priority: str, fire: str, source: str, deadline: datetime.date,
                last_modified: datetime.date, created: datetime.date, comments: str):
    """Adds a new todo inside the todos table"""
    with sqlite3.connect("todos.db") as connection :
        cursor = connection.cursor()
        cursor.execute(
            sql="INSERT INTO todos (name, status, priority, fire, source, deadline, last_modified, created, comments) "
            "VALUE (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            parameters=(name, status, priority, fire, source, deadline, last_modified, created, comments)
        )
        connection.commit()

def delete_todo(todo_id:int):
    """Delete a specific todo"""
    with sqlite3.connect("todos.db") as connection:
        cursor = connection.cursor()
        cursor.execute(sql="DELETE FROM todos WHERE id = ?",
                       # There is a comma at the end because the parameters of cursor.execute must be a tuple
                       # So adding a comma makes it a single element tuple
                       parameters=(todo_id,))
        connection.commit()
