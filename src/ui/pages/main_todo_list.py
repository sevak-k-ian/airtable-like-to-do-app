from nicegui import ui
# Import Database tools and data
from src.models.database import TodoDatabase
from src.models.database import AuthorizedPropertiesOptions

# Import UI components
from src.ui.components.filter_bar import FilterBar
from src.ui.components.grouped_todo_lists_column import GroupedTodoListsColumn
from src.ui.components.filter_button import FilterButton

# Import buttons components displayed
from src.ui.buttons.create_new_todo import CreateNewTodoButton
from src.ui.buttons.grouping_property import GroupingPropertyButton

class MainTodoListPage:
    # Retrieve from SQL database all todos
    all_database_todos = TodoDatabase(db_path="../../../todos.db").get_list_all_todos()

    # Create the filtering buttons (no display yet)
    status_button = FilterButton("Status", AuthorizedPropertiesOptions.STATUS_OPTIONS)
    priority_button = FilterButton("Priority", AuthorizedPropertiesOptions.PRIORITY_OPTIONS)
    source_button = FilterButton("Source", AuthorizedPropertiesOptions.SOURCE_OPTIONS)
    fire_or_clock_button = FilterButton("Fire",AuthorizedPropertiesOptions.FIRE_OPTIONS)

    # Create the FilterPart composed of the previously created button (no display yet)
    filter_bar = FilterBar(status_button, priority_button, source_button, fire_or_clock_button)

    # Header bar (display components previously created)
    with ui.row().classes("w-full justify-between items-center p-4 bg-white") as header_row:
        # Display the UI - this establishes callback connections
        filter_bar.display()

        # Create and Display the GroupBy button CTA
        GroupingPropertyButton().display()

        # Create and Display the NewTodo button CTA
        CreateNewTodoButton().display()

    # Display grouped by property todos in a view of collapsible groups
    GroupedTodoListsColumn(all_database_todos, "source").display()

    # Display the NiceGUI components
    ui.run(language='fr')

if __name__ in {"__main__", "__mp_main__"}:
    MainTodoListPage()