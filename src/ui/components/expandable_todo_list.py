"""
Todo Display Components Module

This module provides UI components for displaying todo items in a NiceGUI application.
It follows a component-based architecture where each class is responsible for rendering
a specific part of the todo list interface.

Architecture:
    - TodoRow: Renders individual todo items as rows
    - SubListMiniHeader: Renders column headers for todo lists
    - ExpandableGroup: Renders collapsible groups of todos with headers

Design Decisions:
    - Separation of concerns: Each class handles one UI responsibility
    - Data transformation happens at the boundary (dict -> Todo object in display())
    - Styling uses Tailwind utility classes for consistency
    - No business logic in display components (presentation only)
"""
import logging
from typing import Any, Optional
from nicegui import ui
from src.models.todo import Todo
from src.styles.constants import STATUS_COLORS, PRIORITY_COLORS

# Configure module-level logger
logger = logging.getLogger(__name__)


class TodoRow:
    """
    Renders a single todo item as a horizontal row with all its properties.

    This component is purely presentational - it receives a Todo object and renders
    it using NiceGUI UI elements. The todo data is converted to a dictionary for
    easier access to properties.

    Design Notes:
        - Stores todo as dict (not object) for simpler property access in display logic
        - Each property has fixed width columns for alignment across rows
        - Hover effect provides visual feedback without requiring JavaScript

    Attributes:
        todo_data (dict[str, Any]): Dictionary representation of the todo item
    """

    def __init__(self, todo: Todo) -> None:
        """
        Initialize TodoRow with a Todo object.

        Args:
            todo (Todo): The todo item to display. Converted to dict internally for easier property access during rendering.

        Raises:
            AttributeError: If todo object doesn't have from_obj_to_dict method
            TypeError: If todo is not a Todo instance
        """
        try:
            self.todo_data = todo.from_obj_to_dict()
            logger.debug(f"TodoRow initialized for todo_id={self.todo_data.get('id', 'unknown')}")
        except AttributeError as error:
            logger.error(f"Todo object missing from_obj_to_dict method: {error}", exc_info=True)
            raise
        except Exception as error:
            logger.error(f"Unexpected error initializing TodoRow: {error}", exc_info=True)
            raise

    def display(self) -> ui.row:
        """
        Render the todo row with all properties in a horizontal layout.

        Layout structure (left to right):
            1. Icon indicator (🔥 or ⏰) - 12 width units
            2. Todo name - flexible width (takes remaining space)
            3. Status pill - 28 width units
            4. Priority pill - 24 width units
            5. Deadline - 32 width units

        Returns:
            ui.row: The NiceGUI row component containing the todo display

        Raises:
            KeyError: If required todo_data keys are missing
        """
        try:
            with ui.row().classes('w-full p-3 items-center hover:bg-gray-50 cursor-pointer text-base') as row:
                # Icon prefix: Fire(urgent) or Clock(scheduled)
                # Empty string if None to avoid displaying "None" text
                icon_display: str = self.todo_data.get("fire_or_clock") or ""
                ui.label(text=icon_display).classes('w-12 text-center text-xl')

                # Todo name: Takes all available space between icon and status
                todo_name: str = self.todo_data.get("todo_name", "Untitled")
                ui.label(todo_name).classes('flex-grow')

                # Status pill: Colored badge showing current status
                status = self.todo_data.get("status", "Unknown")
                status_color = STATUS_COLORS.get(status, "bg-gray-200")
                ui.label(status).classes(
                    f'w-28 text-center text-sm p-1 rounded-full {status_color}')

                # Priority pill: Colored badge showing priority level
                priority = self.todo_data.get("priority", "Unknown")
                priority_color = PRIORITY_COLORS.get(priority, "bg-gray-200")
                ui.label(priority).classes(f'w-24 text-center text-sm p-1 rounded-full {priority_color}')

                # Deadline: Right-aligned date display
                deadline = self.todo_data.get("deadline", "N/A")
                ui.label(deadline).classes('w-32 text-center')

            #  Separator between rows for visual clarity
            ui.separator()

            logger.debug(f"TodoRow displayed for todo_id={self.todo_data.get('id', 'unknown')}")
            return row

        except KeyError as error:
            logger.error(f"Missing required todo_data key: {error}", exc_info=True)
            # Re-raise to let caller handle the error appropriately
            raise
        except Exception as error:
            logger.error(f"Unexpected error displaying TodoRow: {error}", exc_info=True)
            raise


class SubListMiniHeader:
    """
    Renders column headers for todo lists.

    This is a stateless component that only renders the header row. It's implemented
    as a class (rather than a function) for consistency with other display components
    and to allow for future extension (e.g., sortable headers).

    Design Notes:
        - Uses @classmethod because no instance state is needed
        - Column widths match TodoRow columns for alignment
        - Flex-grow spacer aligns headers with data columns
    """

    @classmethod
    def display(cls) -> ui.row:
        """
        Render the column header row.

        The header uses smaller text and muted colors to differentiate from data rows.
        A flex-grow spacer ensures alignment with the todo name column.

        Returns:
            ui.row: The NiceGUI row component containing the headers
        """
        try:
            with ui.row().classes('w-full px-2 py-0 items-center text-xs text-gray-500 font-normal') as header_row:
                # Spacer: Takes up space of icon + todo name to align with data
                # This ensures Status/Priority/Deadline headers align with their columns
                ui.label().classes('flex-grow')

                # Column headers with fixed widths matching TodoRow columns
                ui.label('Status').classes('w-28 text-center')
                ui.label('Priority').classes('w-24 text-center')
                ui.label('Deadline').classes('w-32 text-center')

            logger.debug("SubListMiniHeader displayed")
            return header_row

        except Exception as error:
            logger.error(f"Unexpected error displaying SubListMiniHeader: {error}", exc_info=True)
            raise


class ExpandableGroup:
    """
    Renders a collapsible group of todos with a custom header.

    This component manages a collection of related todos (e.g., grouped by source,
    status, or project). It provides an expansion control to show/hide the todos.

    Design Notes:
        - Stores todos as list for mutability (supports future sorting/filtering)
        - Data transformation (dict -> Todo object) happens during display, not init
          This keeps init lightweight and moves transformation closer to usage
        - Header shows group name and count for quick overview
        - Each group gets its own SubListMiniHeader for clarity

    Attributes:
        todos (List[Dict[str, Any]]): List of todo dictionaries in this group
        group_name (str): Display name for the group (e.g., "Work", "Personal")
        is_group_expanded (bool): Initial expansion state (currently unused by NiceGUI)
    """

    def __init__(self, *todos: dict[str, Any], group_name: str, is_group_expanded: bool = False) -> None:
        """
        Initialize an expandable group of todos.

        Args:
            *todos: Variable number of todo dictionaries to include in this group.
                   Using *args allows flexible group creation: ExpandableGroup(todo1, todo2, ...)
            group_name (str): Display name for the group header
            is_group_expanded (bool, optional): Whether group should start expanded.
                                               Defaults to False (collapsed).

        Raises:
            ValueError: If group_name is empty
            TypeError: If todos are not dictionaries
        """
        if not group_name or not group_name.strip():
            logger.error("ExpandableGroup initialized with empty group_name")
            raise ValueError("group_name cannot be empty")

        try:
            # Store as list for mutability (allows sorting/filtering later)
            self.todos = list(todos)
            self.is_group_expanded = is_group_expanded
            self.group_name = group_name

            logger.info(
                f"ExpandableGroup '{group_name}' initialized with {len(self.todos)} todos, "
                f"expanded={is_group_expanded}"
            )

        except TypeError as error:
            logger.error(f"Invalid todos provided to ExpandableGroup: {error}", exc_info=True)
            raise

    def display(self) -> ui.expansion:
        """
        Render the expandable group with header and todos.

        The header displays:
            - Group name in a gray badge
            - Count of todos in muted text

        When expanded, shows:
            - Column headers (SubListMiniHeader)
            - All todos as TodoRow components

        Returns:
            ui.expansion: The NiceGUI expansion component containing the group

        Design Decision - Data Transformation:
            We convert todo dicts to Todo objects HERE (during display) rather than
            in __init__ because:
            1. Keeps initialization fast and lightweight
            2. Transformation happens close to where data is used
            3. Makes it easier to implement lazy rendering in the future
            4. Reduces memory footprint if group is never displayed

        Raises:
            Exception: If todo transformation or display fails
        """
        try:
            with ui.expansion().props("switch-toggle-side").classes('w-full text-base') as group_expansion:
                # Custom header with group name and todo count
                with group_expansion.add_slot("header"):
                    with ui.row().classes("items-center"):
                        ui.label(f'{self.group_name}').classes("bg-gray-200 rounded px-2 py-1")
                        ui.label(str(len(self.todos))).classes("ml-1 text-gray-500")

                # Content area: column header + todo rows
                with ui.column().classes('w-full gap-0'):
                    SubListMiniHeader().display()

                    # Transform and display each todo
                    # CRITICAL: Transformation happens here to keep init lightweight
                    for todo_dict in self.todos:
                        try:
                            # Convert dict back to Todo object for type safety
                            todo_object = Todo.from_dict_to_obj(todo_dict)
                            todo_row = TodoRow(todo_object)
                            todo_row.display()

                        except (AttributeError, TypeError, KeyError) as error:
                            # Log individual todo errors but continue displaying others
                            logger.error(f"Failed to display todo in group '{self.group_name}': "
                                         f"todo_id={todo_dict.get('id', 'unknown')}, error={error}", exc_info=True)
                            # Continue to next todo instead of breaking entire group
                            continue

            logger.info(f"ExpandableGroup '{self.group_name}' displayed with {len(self.todos)} todos")
            return group_expansion

        except Exception as error:
            logger.error(f"Critical error displaying ExpandableGroup '{self.group_name}': {error}", exc_info=True)
            raise


##########################################
##########################################
if __name__ in {"__main__", "__mp_main__"}:
    """
        Development test runner with sample data.

        This section demonstrates component usage and provides visual testing
        during development. Not executed when module is imported.
        """

    # Configure logging for development
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("Starting TodoRow development test")

    # Sample todo data for testing different states
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
            "source": "🔒 Perso",
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
            "source": "🔒 Perso",
            "deadline": "30/11/2024",
            "modified_time": "25/11/2024 08:00",
            "created_time": "25/11/2024 08:00",
            "comments": "",
            "attachment_dir": "contacts/services"
        }
    ]

    # Test expandable group with sample data
    try:
        ExpandableGroup(
            SAMPLE_TODOS[0],
            SAMPLE_TODOS[3],
            SAMPLE_TODOS[1],
            group_name="🔒 Perso"
        ).display()
        logger.info("ExpandableGroup test completed successfully")
    except Exception as e:
        logger.error(f"ExpandableGroup test failed: {e}", exc_info=True)

    # Uncommented alternative tests for individual components:

    # # Test 1: Single todo row
    # try:
    #     test_todo = Todo.from_dict_to_obj(SAMPLE_TODOS[0])
    #     test_todo_row = TodoRow(test_todo)
    #     SubListMiniHeader.display()
    #     test_todo_row.display()
    #     logger.info("Single TodoRow test completed successfully")
    # except Exception as e:
    #     logger.error(f"TodoRow test failed: {e}", exc_info=True)

    ui.run(language='fr')


