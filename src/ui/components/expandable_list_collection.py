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
from typing import Optional
from nicegui import ui

from gui import main_container
from src.ui.components.expandable_todo_list import ExpandableGroup

# Configure module-level logger
logger = logging.getLogger(__name__)

# Valid grouping properties that can be used to organize todos
# Helps catch typos and documents intended grouping dimensions
VALID_GROUPING_PROPERTIES = {"source", "status", "priority", "deadline", "fire_or_clock"}

class GroupedTodoListsColumn:
    """
    Container component that displays multiple expandable todo groups in a vertical column.
    
    This is a composition component that manages the layout and rendering of multiple
    ExpandableGroup instances. It doesn't handle individual todo logic - that's delegated
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
        expandable_groups (List[ExpandableGroup]): List of groups to display vertically
        grouping_property (str): The property used to create these groups (e.g., "status")
    """
    def __init__(self,*expandable_groups: ExpandableGroup, grouping_property:str) -> None:
        """
        Initialize the grouped todo lists column.

        Args:
            *expandable_groups: Variable number of ExpandableGroup instances to display.
                               Using *args allows flexible composition:
                               GroupedTodoListsColumn(group1, group2, group3, ...)
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

        # Validate that all items are ExpandableGroup instances
        # WHY validate here? Fail fast - catch type errors at initialization, not during display
        for index, group in enumerate(expandable_groups):
            if not isinstance(group, ExpandableGroup):
                logger.error(
                    f"Invalid group at index {index}: expected ExpandableGroup, "
                    f"got {type(group).__name__}"
                )
                raise TypeError(
                    f"All expandable_groups must be ExpandableGroup instances. "
                    f"Item at index {index} is {type(group).__name__}"
                )

        # Store as list for mutability (allows adding/removing groups later)
        # WHY list()? Converts tuple from *args to list, enabling future modifications
        self.expandable_groups: list[ExpandableGroup] = list(expandable_groups)
        self.grouping_property : str = grouping_property

        logger.info(
            f"GroupedTodoListsColumn initialized with {len(self.expandable_groups)} groups, "
            f"grouped by '{grouping_property}'"
        )

    def display(self):
        """
        Render all expandable groups in a vertical column layout.

        The column takes full width and stacks groups vertically. Each group is
        independently expandable/collapsible.

        Returns:
            ui.column: The NiceGUI column component containing all groups

        Raises:
            Exception: If any group fails to display (re-raised after logging)

        Design Decision - Error Handling Strategy:
            We continue rendering even if one group fails. WHY?
            - Better user experience: show what we can, even if some data is broken
            - Easier debugging: see which groups work and which don't
            - Graceful degradation: partial functionality beats complete failure

        Alternative Approach (not used):
            We could fail fast and stop on first error. This would be appropriate if:
            - All groups must be present (business requirement)
            - Partial display would confuse users more than an error message
            - Groups have dependencies on each other
        """
        try:
            with ui.column().classes("w-full") as column_container:
                #Render each group, continuing even if individual groups fail
                successful_displays = 0
                
                for index, expandable_group in enumerate(self.expandable_groups):
                    try:
                        expandable_group.display()
                        successful_displays += 1

                    except Exception as error:
                        # Log the error with context but continue to next group
                        # WHY continue? One broken group shouldn't break the entire UI
                        logger.error(
                            f"Failed to display group at index {idx} in "
                            f"GroupedTodoListsColumn (grouping='{self.grouping_property}'): {e}",
                            exc_info=True
                        )

                        # Optionally: Display an error placeholder for this group
                        # This shows users that a group exists but failed to load
                        with ui.card().classes("w-full p-4 bg-red-50 border border-red-200"):
                            ui.label("⚠️ Failed to load this group").classes("text-red-600 font-semibold")
                            ui.label(f"Error: {str(e)}").classes("text-sm text-red-500")

                        continue

            logger.info(
                f"GroupedTodoListsColumn displayed: {successful_displays}/{len(self.expandable_groups)} "
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
