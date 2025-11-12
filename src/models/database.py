"""
Todo Database Manager

This module provides a DB management system for a todo app.
It included : DB operations, table management & CRUD operations for todos.

Dependencies :
- sqlite3 : for DB operations
- contextlib : for connection context management
- typing : for type hints and optional values
"""

import sqlite3
from contextlib import contextmanager
import logging
from pathlib import Path
import datetime  # for "now"
import pytz  # for "timezone"

DB_COLS = ['id', 'todo_name', 'status', 'priority', 'fire_or_clock', 'source', 'deadline', 'modified_time',
           'created_time', 'comments', 'attachment_dir']

# Database schema definition - defines the 11 cols of the todos table
logging.basicConfig(level=logging.DEBUG)  # All levels of infos are shown now for testing purpose, can turn this

# Set up logging for DB operations
# Instead of print("Something happened"), I write logger.info("Something happened")
# I can easily turn logging on/off, save logs to files, and have different log levels (DEBUG, INFO, WARNING, ERROR).
# to WARNING level for production
logger = logging.getLogger(__name__)


class AuthorizedPropertiesOptions:
    STATUS_OPTIONS = ["Todo", "Done"]
    PRIORITY_OPTIONS = ["High", "Medium", "Low"]
    SOURCE_OPTIONS = ["🔒 Perso", "👩‍❤️‍👨 Famille", "👶 Yeraz", "🤱 Mama", "💼 Hameaux Légers"]
    FIRE_OPTIONS = ["🔥", "⏰", ""]


class DatabaseError(Exception):
    """Custom exception class for DB-related errors."""
    pass


class DatabaseManager:
    """
    Base class for managing general DB and table management operations.

    This class provides core DB functionality including connection management, table creation, and schema modifications.
    It serves as the foundation for more specific DB operations.

    Attributes :
        db_path (str / Path) : Path to the SQLite DB file
        table_name (str) : Name of the primary table (default : "todos")

    Example :
        db_manager = DatabaseManager("my_todos.db")
        db_manager.initialize_new_table("todos")
        print(db_manager.get_db_name())
    """

    # INIT OBJECT
    def __init__(self, db_path: str | Path, table_name: str = "todos"):
        """
        Initialize the DatabaseManager with a DB path and table name.

        Args:
            db_path (str/Path): Path of the SQLite DB file
            table_name (str): Name of the primary table (default : "todos")

        Raises:
             DatabaseError: if the DB path is invalid or inaccessible
        """
        self.db_path = Path(db_path) if isinstance(db_path, str) else db_path
        self.table_name = table_name

        # Validate DB path and create directory if needed
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            logger.error(f"🛑Failed to create DB dir: {error}")
            raise DatabaseError(f"Cannot create DB dir: {error}")

        logger.info(f"✅DatabaseManager initialized with path : {self.db_path}")

    # PRIVATE METHODS
    def _get_conn(self) -> sqlite3.Connection:
        """
        Create and return a basic SQLite connection.

        Private method used internally by other DB operations.
        The connection uses default row factory (tuples).

        Returns:
            sqlite3.Connection: DB connection object

        Raises:
            DatabaseError: if connection cannot be established
        """
        try:
            conn = sqlite3.connect(database=str(self.db_path))
            # Enable foreign key constraints (in case multiple tables exist)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn  # I don’t use yield because I don’t wait for client-server side data, like for CRUD operations
        except sqlite3.Error as error:
            logger.error(f"🛑Failed to connect to DB: {error}")
            raise DatabaseError(f"DB connection failed: {error}")

    @contextmanager
    def _get_conn_dict_mode(self):
        """
        Context manager that provides a DB connection with dictionary row factory.

        This connection returns rows as sqlite3.Row objects, which can be accessed like dictionaries (row["col_name"]) or
        by index (row[0]).
        Automatically handles connection clean and rollback on errors.

        Yields:
            sqlite3.Connection: DB connection with Row factory

        Raises:
            DatabaseError: if connection fails or DB operation errors occur

        """
        conn = None
        try:
            # Create connection with row factory for dictionary-like accesse
            conn = sqlite3.connect(database=str(self.db_path))
            conn.row_factory = sqlite3.Row  # Enable dict-like row access
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys

            logger.info("✅DB connection established with dict mode")
            yield conn

        except sqlite3.Error as error:
            # Rollback any pending transaction on error
            if conn:
                conn.rollback()
            logger.error(f"🛑Database operation failed: {error}")
            raise DatabaseError(f"Database operation failed: {error}")

        finally:
            # Always close connection, even if error occured
            if conn:
                conn.close()
                logger.info("✅DB connection closed.")

    def _resolve_table_name(self, table_name: str | None) -> str:
        """
        Resolve table name to use, defaulting to instance table name if None provided.

        Args:
            table_name (str | None): Table name to use, or None for default

        Returns:
            str: The resolved table name to use
        """
        if table_name is None:
            table_name = self.table_name  # (='todos' name, set by DatabaseManager object init method)
        return table_name

    # PUBLIC METHODS
    def get_db_full_path(self) -> str:
        """
        Get the full path of the DB file as a string.

        Returns:
            str: full path to the DB

        Example:
            db_manager = DatabaseManager("./data/todos.db")
            print(db_manager.get_db_full_path())
            → '/full/path/to/data/todos.db'

        """
        return str(self.db_path.resolve())

    def db_exists(self) -> bool:
        """
        Check if the database file exists on disk.

        Returns:
            bool: True if database file exists, False otherwise
        """
        return self.db_path.exists()

    def initialize_new_table(self, table_name: str | None = None) -> None:
        """
        Create the main todos table if it doesn't exist.

        This method creates a table with all necessary columns for todo management.
        The table includes fields for task details, metadata, and file attachments.
        Uses IF NOT EXISTS to avoid errors if table already exists.

        Args:
            table_name (str, optional): Name of table to create. Uses self.table_name if None.

        Raises:
            DatabaseError: If table creation fails

        Table Schema:
            - id: Primary key (auto-increment integer)
            - todo_name: Task description (required text)
            - status: Current status (required text)
            - priority: Task priority (optional text)
            - fire_or_clock: Urgency indicator (optional text)
            - source: Task source/category (optional text)
            - deadline: Due date (optional text)
            - modified_time: Last modification timestamp (optional text)
            - created_time: Creation timestamp (optional text)
            - comments: Additional notes (optional text)
            - attachment_dir: Path to attachments (optional text)
        """
        # Option 1 : use the default DatabaseManager table name "todos" if no args is provided
        self._resolve_table_name(table_name)

        # Option 2 : use user's provided table name to create a new table in the database, that will be existing with 'todos' table
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                # SQL query to create the todos table with comprehensive schema
                query: str = f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    todo_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT,
                    fire_or_clock TEXT,
                    source TEXT,
                    deadline TEXT,
                    modified_time TEXT,
                    created_time TEXT,
                    comments TEXT,
                    attachment_dir TEXT
                )
            '''

                cursor.execute(query)
                conn.commit()
                logger.info(f"✅Table '{table_name}' initialized successfully.")

        except sqlite3.Error as error:
            logger.error(f"🛑Failed to initialize table '{table_name}': {error}")
            raise DatabaseError(f"Table initialization failed: {error}")

    def print_all_existing_columns(self, table_name: str | None = None) -> str:
        """
        Print all column names in the specified table to console.

        Useful for debugging and understanding the current table structure.
        Uses SQLite's PRAGMA table_info command.

        Args:
            table_name (str, optional): name of table to inspect. Uses self_table_name if None ('todos' table).

        Raises:
            DatabaseError: if table doesn't exist or query fails.

        Note:
            PRAGMA table_info returns columns with structure:
            [0]=cid, [1]=name, [2]=type, [3]=notnull, [4]=default, [5]=pk
        """
        # Use the default DatabaseManager table name "todos" if no args is provided
        self._resolve_table_name()

        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                # Get table schema information using PRAGMA
                cursor.execute("PRAGMA table_info(todos)")
                columns_info = cursor.fetchall()

                if not columns_info:
                    print(f"⚠️Table '{table_name}' does not exist or has no columns")
                    return

                # Extract column names (index 1 in PRAGMA result)
                cols_name = [column[1] for column in columns_info]

                logger.info(f"📋 Current existing columns in '{table_name}': {cols_name}")
                logger.info(f"✅Retrieved {len(cols_name)} columns from table '{table_name}'")

        except sqlite3.Error as error:
            logger.error(f"🛑Failed to retrieve columns from '{table_name}': {error}")
            raise DatabaseError(f"Column retrieval failed: {error}")

    def get_table_cols(self, table_name: str | None = None) -> list[str]:
        """
        Get list of column names in the specified table.

        Args:
            table_name (str, optional): Name of table to inspect. Uses self.table_name if None.

        Returns:
            List[str]: List of column names

        Raises:
            DatabaseError: If table doesn't exist or query fails
        """
        # Use the default DatabaseManager table name "todos" if no args is provided
        self._resolve_table_name(table_name)

        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                # Get table schema information using PRAGMA
                cursor.execute(f"PRAGMA table_info({table_name})")
                cols = [column[1] for column in cursor.fetchall()]

                logger.info(f"✅Retrieved {len(cols)} cols from table {table_name}")
                logger.info(f"List of cols is : {cols}")

                return cols
        except sqlite3.Error as error:
            logger.error(f"🛑Failed to retrieve columns from '{table_name}': {error}")
            raise DatabaseError(f"Column retrieval failed: {error}")

    def create_new_col(self, col_name: str, col_type: str, table_name: str | None = None) -> None:
        """
        Add a new column to the specified table if it does not already exist.

        This method safely adds new columns using ALTER TABLE ADD COLUMN.
        It first checks if the column exists to avoid duplicate column errors.

        Args:
            col_name (str): name of the column to add
            col_type(str): SQL data type for the new column (eg : "TEXT", "INT", etc)
            table_name (str, optional): name of table to modify. Uses self.table_name if None.

        Raises:
            DatabaseError: if column creation fails
            ValueError: if col_name or col_type are invalid

        Example:
            db_manager.create_new_col('tags', 'TEXT')
            db_manager.create_new_col('completed_date', 'DATETIME')
        """
        # Check errors on provided (or non provided) col name and type args
        if not col_name or not col_name.strip():
            raise ValueError("⚠️Column name connot be empty.")
        if not col_type or not col_type.strip():
            raise ValueError("⚠️Column type cannot be empty.")

        # Affects a table_name if None is provided
        if table_name is None:
            table_name = self.table_name

        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                # Get the list of current columns in the table
                cursor.execute("PRAGMA table_info(todos)")
                existing_columns = [column[1] for column in cursor.fetchall()]

                # Check if col to create already exists or is missing
                if col_name not in existing_columns:
                    print(f"🚧 Updating table '{table_name}' : adding column '{col_name}'")

                    # Use parameterized query carefully - table/column names can't be parameterized
                    # But we validate input above to prevent injection`
                    cursor.execute(f"ALTER TABLE todos ADD COLUMN {col_name} {col_type}")
                    conn.commit()
                    logger.info(f"✅Added column '{col_name}' to table '{table_name}'")
                else:
                    logger.info(f"⚠️Column '{col_name} already exists - skipping creation'")
                    logger.info(f"The existing columns are : {existing_columns}")

        except sqlite3.Error as error:
            logger.error(f"🛑Failed to create column '{col_name}' in table '{table_name}': {error}")
            raise DatabaseError(f"Column creation failed: {error}")

    def delete_existing_col(self, col_name: str, table_name: str | None = None):
        """
        Delete a column from the specified table if column exists.

        This method safely deletes columns using ALTER TABLE DROP COLUMN.
        It first checks if the column exists to avoid database errors.
        SQLite's ALTER TABLE DROP COLUMN was added in version 3.35.0 (2021).
        For older SQLite versions, this operation requires recreating the table.

        Args:
            col_name (str): name of the column to add
            table_name (str, optional): name of table to modify. Uses self.table_name if None.

        Raises:
            DatabaseError: if column deletion fails
            ValueError: If col_name is invalid

        Example:
            db_manager.delete_existing_col('tags', 'owner')
            db_manager.delete_existing_col("deadline")
        """
        if not col_name or not col_name.strip():
            raise ValueError("⚠️Column name cannot be empty")

        if table_name is None:
            table_name = self.table_name

        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                # Get the list of current columns in table
                cursor.execute("PRAGMA table_info(todos)")
                existing_columns = [column[1] for column in cursor.fetchall()]

                # Only attempt deletion if column exists
                if col_name in existing_columns:
                    print(f"🚧Found column '{col_name}' to delete in table '{table_name}'")

                    query = f"ALTER TABLE  {table_name} DROP COLUMN {col_name}"
                    cursor.execute(query)
                    conn.commit()
                    logger.info(f"✅Deleted column '{col_name}' in table '{table_name}'")

                else:
                    logger.info(
                        f"⚠️Skipped column deletion. Column '{col_name}' doesn't exist in table '{table_name}'")
                    logger.info(f"The existing columns in table '{table_name}' are : {existing_columns}")

        except sqlite3.Error as error:
            # Handle case where SQLite version doesn't support DROP COLUMN
            if "no such column" in str(error).lower() or "drop column" in str(error).lower:
                logger.error(f"🛑SQLite version may not support DROP COLUMN: {error}")
                raise DatabaseError(f"Column deletion not supported or column doesn't exist: {error}")
            else:
                logger.error(f"🛑Failed to deleted column '{col_name}' in table '{table_name}': {error}")
                raise DatabaseError(f"Column deletion failed: {error}")


class TodoDatabase(DatabaseManager):
    """"
    Specialized database manager for todo operations and CRUD functionality.

    This class extends DatabaseManager to provide specific operations for managing
    todo items including creation, retrieval, updating, and deletion of tasks.
    It handles all the business logic for todo management while inheriting
    the core database functionality from its parent class.

    Attributes:
        Inherits all attributes from DatabaseManager (db_path and table_name)

    Example:
        todo_db = TodoDatabase("my_todos.db")
        todos = todo_db.get_list_all_todos()
        new_id = todo_db.create_todo("Buy groceries", "Todo", "High", ...)
    """

    # INIT OBJECT
    def __init__(self, db_path: str | Path = "../../todos.db", table_name: str = "todos"):
        """
        Initialize TodoDatabase and ensure the todos table exists.

        This constructor calls the parent DatabaseManager constructor and then automatically creates the todos table if
        it doesn’t exist.

        Args:
             db_path (str/Path): path to the SQLite database file (default: "todos.db")
             table_name (str) : name of the todos table (default: "todos")

        Raises:
            DatabaseError: if database initialization or table creation fails
        """
        # Call parent constructor to initialize database connection
        super().__init__(db_path, table_name)

        # Automatically initialize the todos table
        try:
            self.initialize_new_table("todos")
            logger.info(f"✅TodoDatabase initialized successfully with table '{self.table_name}'")
        except DatabaseError as error:
            logger.error(f"🛑Failed to initialize TodoDatabase: {error}")
            raise

    def _validate_col_name(self, col_name: str) -> None:
        """
        Raises ValueError(s) if column name is not a string or is not allowed.

        Args:
            col_name (str): Column name to validate

        Raises:
            ValueError: If col_name is not valid or not allowed.
        """
        # Check if string provided
        if not isinstance(col_name, str) or not col_name.strip():
            raise ValueError("⚠️Column name must be a non-empty string.")

        allowed_cols: list = ["todo_name", "status", "priority", "fire_or_clock", "source", "deadline", "comments",
                              "attachment_dir"]

        # Check if col_name provided is allowed
        if col_name not in allowed_cols:
            raise ValueError(
                f"⚠️Col name '{col_name}' provided is not allowed. "
                f"Allowed col names for table '{self.table_name}' are : {allowed_cols}")

    def _validate_todo_id(self, todo_id: int) -> None:
        """
        Raise error if todo_id is not a valid positive integer.

        Args:
            todo_id (int): ID to validate

        Raises:
            TypeError: if todo_id is not an integer
            ValueError: if todo_id is not a int or not superior to zero
        """
        if not isinstance(todo_id, int):
            raise TypeError("⚠️todo_id must be an integer")

        if todo_id <= 0:
            raise ValueError(f"⚠️todo_is must be strictly superior to 0")

    def _validate_todo_name(self, todo_name: str) -> None:
        """
        Raise error if todo_name is empty.

        Args:
            todo_name (str): todo name to validate

        Raises:
            ValueError: if todo_name is empty
        """
        if not todo_name or not todo_name.strip():
            raise ValueError(f"⚠️todo_name is invalid, need to be a non-empty string.")

    def _get_now_date(self, with_time: bool | None = False) -> str:
        """
        Get now FR formatted date with or without time.

        Args:
            with_time: True if need to integrate now time in the string output.

        Raises:
            ValueError: if with_time is not a boolean
        """
        if not isinstance(with_time, bool):
            raise ValueError(f"⚠️with_time must be a boolean value.")

        current_fr_time: datetime = datetime.datetime.now(pytz.timezone("Europe/Paris"))

        if with_time:
            return current_fr_time.strftime(format="%d/%m/%Y %H:%M")
        else:
            return current_fr_time.strftime(format="%d/%m/%Y")

    # PUBLIC METHODS
    def get_list_all_todos(self) -> list[dict[str, any]]:
        """
        Retrieve all todo items from the database.

        This method fetches all records from the todos table and returns them
        as a list of dictionaries for easy manipulation and display.

        Returns:
            List[Dict[str, Any]]: List of todo dictionaries, each containing all columns

        Raises:
            DatabaseError: If the query fails or database is inaccessible

        Example:
            todos = todo_db.get_list_all_todos()
            for todo in todos:
            ...     print(f"Task: {todo['todo_name']}, Status: {todo['status']}")
        """
        try:
            with self._get_conn_dict_mode() as conn:
                cursor = conn.cursor()

                # Select all records from todos table
                query: str = "SELECT * FROM todos"
                cursor.execute(query)

                current_todos: list = [dict(row) for row in cursor.fetchall()]

                logger.info(f"✅Retrieved {len(current_todos)} todos from database.")
                return current_todos

        except DatabaseError as error:
            logger.error(f"🛑Failed to get list of all current todos: {error}")
            raise

    def get_todo_by_id(self, todo_id: int) -> sqlite3.Row | None:
        """
        Retrieve a specific todo item by its unique ID.

        Args:
            todo_id (int) : the unique identifier of the todo item.

        Returns:
        Optional[sqlite3.Row]: Todo record as Row object, or None if not found

        Raises:
            TypeError: If todo_id is not an integer
            ValueError: If todo_id is not greater than zero
            DatabaseError: If the query fails

        Example:
            todo = todo_db.get_todo_by_id(5)
            if todo:
            ...     print(f"Found: {todo['todo_name']}")
            ... else:
            ...     print("Todo not found")
        """
        # Check if todo_id arg is valid and raises error if not
        self._validate_todo_id(todo_id)

        try:
            with self._get_conn_dict_mode() as conn:
                cursor = conn.cursor()

                # Use parameterized query to prevent SQL injection
                query: str = f"SELECT * FROM {self.table_name} WHERE id = ?"
                cursor.execute(query, (todo_id,))
                result = cursor.fetchone()

                if result:
                    logger.info(f"✅Retrieved todo with ID {todo_id}")
                else:
                    logger.info(f"✅No todo found with ID {todo_id}")

                return result

        except DatabaseError as error:
            logger.error(f"🛑Failed to retrieve todo item with todo_id {todo_id}: {error}")
            raise

    def get_todo_id_via_name(self, todo_name: str) -> int | None:
        """
        Find the ID of a todo item by searching for its name.

        This method performs an exact match search on the todo_name field.
        If multiple todos have the same name, it returns the ID of the first match.

        Args:
            todo_name (str): The exact name of the todo to search for

        Returns:
            int|None: The ID of the matching todo, or None if not found

        Raises:
            DatabaseError: If the query fails
            ValueError: If todo_name is empty or invalid

        Example:
            todo_id = todo_db.get_todo_id_via_name("Buy groceries")
            if todo_id:
                print(f"Found todo with ID: {todo_id}")
        """
        # Raise error and stop method if todo_name is empty
        self._validate_todo_name(todo_name)

        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                # Search for exact match of todo name
                query: str = f"SELECT id FROM {self.table_name} WHERE todo_name = ?"
                cursor.execute(query, (todo_name.strip(),))
                result = cursor.fetchone()

                if result:
                    todo_id = result[0]
                    logger.info(f"✅Retrieved one todo from table '{self.table_name}' with ID {todo_id}")
                    return todo_id
                else:
                    logger.info(f"✅No todo found with name '{todo_name}'")
                    return None

        except DatabaseError as error:
            logger.error(f"🛑Failed to search for todo '{todo_name}': {error}")
            raise

    def create_todo(self,
                    todo_name: str,
                    status: str,
                    priority: str = "",
                    fire_or_clock: str = "",
                    source: str = "",
                    deadline: str = "",
                    comments: str = "",
                    attachment_dir: str = "") -> int:
        """
        Create a new todo item in the database.

        This method inserts a new todo record with all specified fields.
        Only todo_name and status are required; all other fields are optional.
        created_time and modified_time are not listed as args because they are always created inside the method
        at execution moment.

        Args:
            todo_name (str): Description of the task (required)
            status (str): Current status of the task (required)
            priority (str): Priority level (optional)
            fire_or_clock (str): Urgency indicator emoji (optional)
            source (str): Source or category of the task (optional)
            created_time (str): Date at the moment of todo creation by gui (compulsory in GUI)
            modified_time (str) : Last date of modification of any sort. Initially takes created_time's value at creation moment.
            deadline (str): Due date for the task (optional)
            comments (str): Additional notes about the task (optional)
            attachment_dir (str): Path to related files (optional)

        Returns:
            int: The ID of the newly created todo item

        Raises:
            DatabaseError: If the insertion fails
            ValueError: If required fields are empty or invalid

        Example:
            new_id = todo_db.create_todo(
                 todo_name="Complete project",
                 status="Todo",
                 priority="High",
                 deadline="2024-12-31"
             )
            print(f"Created todo with ID: {new_id}")
        """
        # Validate required non-empty fields
        self._validate_todo_name(todo_name)

        if not status or not status.strip():
            raise ValueError(f"⚠️status is required and cannot be empty.")

        # Validate status against allowed options
        if status not in AuthorizedPropertiesOptions.STATUS_OPTIONS:
            logger.warning(
                f"⚠️Status '{status}' is not in predefined options: {AuthorizedPropertiesOptions.STATUS_OPTIONS}")
            raise ValueError(
                f"Status '{status}' is not in predefined options: '{AuthorizedPropertiesOptions.STATUS_OPTIONS}'")

        # Creation date value
        created_time = self._get_now_date(with_time=False)

        # Last modified date & time value
        modified_time = self._get_now_date(with_time=True)

        # SQL Query
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                query: str = f"""INSERT INTO {self.table_name} (todo_name, status, priority, fire_or_clock, source, deadline, 
                                modified_time, created_time, comments, attachment_dir) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                cursor.execute(query, (
                    todo_name.strip(),
                    status.strip(),
                    priority.strip(),
                    fire_or_clock.strip(),
                    source.strip(),
                    deadline.strip(),
                    modified_time.strip(),
                    created_time.strip(),
                    comments.strip(),
                    attachment_dir
                ))

                # Get the ID of the newly inserted record
                new_todo_id = cursor.lastrowid
                conn.commit()

                logger.info(f"✅Created new todo '{todo_name}' with ID {new_todo_id}")
                return new_todo_id

        except sqlite3.Error as error:
            logger.error(f"🛑Failed to create todo '{todo_name}': {error}")
            raise DatabaseError(f"Could not create todo: {error}")

    def delete_todo(self, todo_id: int) -> bool:
        """
        Delete a todo item from the database by its ID.

        This operation permanently removes the todo record and cannot be undone.
        Consider backing up your database before performing deletions.

        Args:
            todo_id (int): The unique identifier of the todo to delete

        Returns:
            bool: True if a todo was deleted, False if no todo found with that ID

        Raises:
            DatabaseError: If the deletion fails
            ValueError: If todo_id is not a valid positive integer

        Example:
            success = todo_db.delete_todo(5)
            if success:
                print("Todo deleted successfully")
            else:
                print("Todo not found")
        """
        self._validate_todo_id(todo_id)

        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

                # Delete the todo with the specified ID
                cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?",
                               # There is a comma at the end because the parameters of cursor.execute must be a tuple
                               # So adding a comma makes it a single element tuple
                               (todo_id,))

                # Check if any rows were actually deleted
                rows_affected = cursor.rowcount
                conn.commit()

                if rows_affected > 0:
                    logger.info(f"✅Successfully deleted todo with ID {todo_id}")
                    return True
                else:
                    logger.info(f"✅No todo found with ID {todo_id} - nothing deleted")
                    return False

        except sqlite3.Error as error:
            logger.error(f"🛑Failed to delete todo with ID '{todo_id}': {error}")
            raise DatabaseError(f"Could not delete todo: {error}")

    def update_one_col(self, todo_id: int, col_to_update: str, new_value: any) -> None:
        """
        Update a single column of a specific todo item.

        This method allows you to modify one field of a todo without affecting
        other fields. It includes validation to ensure only allowed columns are updated.

        Args:
            todo_id (int): The unique identifier of the todo to update
            col_to_update (str): Name of the column to update
            new_value (Any): New value to set for the specified column

        Raises:
            DatabaseError: If the update fails or todo doesn't exist
            ValueError: If parameters are invalid or column is not allowed

        Example:
            todo_db.update_one_col(5, "status", "Done")
            todo_db.update_one_col(3, "priority", "High")
            todo_db.update_one_col(1, "comments", "Updated notes")
        """
        # Validate (or raise errors) for required args
        self._validate_col_name(col_to_update)

        self._validate_todo_id(todo_id)

        current_time = self._get_now_date(True)

        try:
            with (self._get_conn() as conn):
                cursor = conn.cursor()

                query: str = f"""
                UPDATE todos SET
                    {col_to_update} = ?,
                    modified_time = ?         
                WHERE id = ?
                """
                cursor.execute(query, (new_value.strip(), current_time.strip(), todo_id))
                conn.commit()

            print(f"✅Updated column {col_to_update} for todo N°{todo_id}. "
                  f"New value written: '{new_value}'")

        except DatabaseError as error:
            logger.error(f"🛑Couldn't update colum '{col_to_update}' for todo_id '{todo_id}': {error}")
            raise DatabaseError(f"Could not update todo: {error}")

    def update_entire_todo(self, todo_id: int, todo_name: str, status: str, priority: str, fire_or_clock: str,
                           source: str,
                           deadline: str, comments: str) -> int:
        """
        Update all the todo properties in database, except attachment_dir that is determined at creation, and can't be changed.

        This method allows you to modify all fields of a todo (except 'created_time' value). It includes validation to
        ensure proper functioning.

        Args:
            todo_id (int): the unique identifier of the todo item.
            todo_name (str): Description of the task (required)
            status (str): Current status of the task (required)
            priority (str): Priority level (optional)
            fire_or_clock (str): Urgency indicator emoji (optional)
            source (str): Source or category of the task (optional)
            deadline (str): Due date for the task (optional)
            comments (str): Additional notes about the task (optional)

        Returns:
            todo_id : int

        Raises:
            DatabaseError: if the updating fails
            ValueError : if required fields are empty or invalid
        """
        # Validate (or raise errors) for required args
        self._validate_todo_id(todo_id)

        self._validate_todo_name(todo_name)

        if not status or not status.strip():
            raise ValueError("⚠️status is required and cannot be empty.")

        current_time = self._get_now_date(True)

        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()

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
                                    id = ?;
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
                    current_time.strip(),
                    todo_id  # This corresponds to the final '?' in the WHERE clause.
                )

                cursor.execute(query, values_tuple)
                conn.commit()

            logger.info(f"✅ Successfully updated todo with ID: {todo_id}.")
            return int(todo_id)

        except sqlite3.Error as error:
            logger.error(f"🛑Failed to update todo with ID '{todo_id}': {error}")
            raise DatabaseError(f"Could not update todo: {error}")


# DUMMY DATA
todo_test = {
    "todo_name": "New date feature TO CREATE",
    "priority": "Medium",
    "source": "🤱 Mama",
    "fire_or_clock": "⏰",  # False for "clock" (scheduled task)
    "deadline": "20/09/2025",
    "status": "Done",
    "files": "no files",
    "comments": "Yazooo",
    "created_time": "17/09/2025",
    "modified_time": "17/09/2025"
}

# TESTING
if __name__ == "__main__":
    todos_database = TodoDatabase()
    todos_database.delete_todo(6)
    todos_database.delete_todo(7)
