"""
Grouped Todo Lists Column Module

This module provides a container component for displaying multiple expandable todo groups
in a vertical column layout. It acts as a composition layer that manages multiple
ExpandableGroup components.

Architecture:
    - GroupedTodoListsColumn: Container that renders multiple ExpandableGroup components
    - Follows composition over inheritance pattern
    - Separates layout concerns (column) from group logic (ExpandableGroup)

Design Decisions:
    - Why store grouping_property?: Enables future features like "regroup by X" buttons,
      displaying the current grouping criterion in UI, or validating that all groups
      match the expected grouping property
    - Why accept *expandable_groups?: Flexible initialization - caller can pass any number
      of groups without creating intermediate lists
    - Why display() not __init__?: Separation of concerns - initialization prepares data,
      display() handles rendering. Allows re-displaying without recreating objects.
"""
import logging
from nicegui import ui
from pprint import pprint

# Valid grouping properties that can be used to organize todos
# Helps catch typos and documents intended grouping dimensions
from src.business_logic.grouping import group_todos_by_property, VALID_GROUPING_PROPERTIES
from src.models.database import TodoDatabase
from src.ui.components.expandable_todo_list import ExpandableGroup

# Configure module-level logger
logger = logging.getLogger(__name__)

class GroupedTodoListsColumn:
    """
    Container component that displays multiple expandable todo groups in a vertical column.
    
    This is a composition component that manages the layout and rendering of multiple
    todos instances. It doesn't handle individual todo logic - that's delegated
    to the ExpandableGroup components.
    
    Design Notes:
        - Acts as a lightweight container - no business logic, just layout
        - Stores grouping_property for future features (e.g., "Grouped by: Status" header)
        - Uses *args pattern for flexible group composition
        - Validates inputs to catch configuration errors early
    
    Use Cases:
        - Display todos grouped by source (Work, Personal, etc.)
        - Display todos grouped by status (Todo, In Progress, Done)
        - Display todos grouped by priority (High, Medium, Low)
    
    Attributes:
        all_todos (List[dict]): List of groups to display vertically
        grouping_property (str): The property used to create these groups (e.g., "status")
    """

    def __init__(self, all_todos: list[dict], grouping_property: str) -> None:
        """
        Initialize the grouped todo lists column.

        Args:
            all_todos: list of todos_data coming from the SQL Database
            grouping_property (str): The property by which todos are grouped.
                                    Examples: "source", "status", "priority"
                                    Used for documentation and potential UI display.

        Raises:
            ValueError: If grouping_property is empty or invalid
            TypeError: If any expandable_groups item is not an ExpandableGroup instance

        Design Decision - Why validate grouping_property?:
            Early validation catches configuration errors before they cause runtime issues.
            For example, if someone typos "satus" instead of "status", we catch it here
            rather than discovering it later when trying to display a grouping header.
        """
        # Validate grouping_property is not empty
        if not grouping_property or not grouping_property.strip():
            logger.error("GroupedTodoListsColumn initialized with empty grouping_property")
            raise ValueError("grouping_property cannot be empty")

        # Validate grouping_property is recognized (helps catch typos)
        # NOTE: This is a soft validation - warns but doesn't fail
        # WHY? Because we want to support custom grouping properties in the future
        if grouping_property not in VALID_GROUPING_PROPERTIES:
            logger.warning(
                f"Grouping property '{grouping_property}' is not in recognized list: "
                f"{VALID_GROUPING_PROPERTIES}. This may be intentional for custom groupings."
            )

        # Validate that all items are todo_data dict
        # WHY validate here? Fail fast - catch type errors at initialization, not during display
        for index, todo_data in enumerate(all_todos):
            if not isinstance(todo_data, dict):
                logger.error(
                    f"Invalid todo_data at index {index}: expected dict"
                )
                raise TypeError(
                    f"All todo_data must be dict. "
                    f"Item at index {index} is {type(todo_data)}"
                )


        # Store as list for mutability (allows adding/removing groups later)
        # WHY list()? Converts tuple from *args to list, enabling future modifications
        self.all_todos: list[dict] = all_todos
        self.grouping_property: str = grouping_property

        logger.info(
            f"GroupedTodoListsColumn initialized"
            f"grouped by '{grouping_property}'"
        )

    def display(self):
        """
        Render all todos into expandable groups of todos in a vertical column layout.

        The column takes full width and stacks groups vertically. Each group is
        independently expandable/collapsible, after being grouped by a method.

        Returns:
            ui.column: The NiceGUI column component containing all groups

        Raises:
            Exception: If any group fails to display (re-raised after logging)

        Design Decision - Error Handling Strategy:
            We continue rendering even if one group fails. WHY?
            - Better user experience: show what we can, even if some data is broken
            - Easier debugging: see which groups work and which don't
            - Graceful degradation: partial functionality beats complete failure

        """
        try:
            todos_grouped_by_property = group_todos_by_property(todos=self.all_todos,
                                                                grouping_property=self.grouping_property)
            with ui.column().classes("w-full") as column_container:
                # Render each group, continuing even if individual groups fail
                successful_displays = 0

                for grouping_key, grouped_todos_dict in todos_grouped_by_property.items():
                    try:
                        ExpandableGroup(*grouped_todos_dict, group_name=grouping_key).display()
                        successful_displays += 1

                    except Exception as error:
                        # Log the error with context but continue to next group
                        # WHY continue? One broken group shouldn't break the entire UI
                        logger.error(
                            f"Failed to display group at index {grouping_key} in "
                            f"GroupedTodoListsColumn (grouping='{self.grouping_property}'): {error}",
                            exc_info=True
                        )

                        # Optionally: Display an error placeholder for this group
                        # This shows users that a group exists but failed to load
                        with ui.card().classes("w-full p-4 bg-red-50 border border-red-200"):
                            ui.label("⚠️ Failed to load this group").classes("text-red-600 font-semibold")
                            ui.label(f"Error: {str(error)}").classes("text-sm text-red-500")

                        continue

            logger.info(
                f"GroupedTodoListsColumn displayed: {successful_displays}/{len(todos_grouped_by_property)} "
                f"groups rendered successfully (grouping='{self.grouping_property}')"
            )
            return column_container

        except Exception as error:
            # Critical error at column level (not individual group)
            logger.error(
                f"Critical error displaying GroupedTodoListsColumn "
                f"(grouping='{self.grouping_property}'): {error}",
                exc_info=True
            )
            raise


if __name__ in {"__main__", "__mp_main__"}:
    all_database_todos = TodoDatabase(db_path="../../../todos.db").get_list_all_todos()
    GroupedTodoListsColumn(all_database_todos, "fire_or_clock").display()
    ui.run(language='fr')
