############# TODOS
# TODO Add an highlight color behind the status' name, or group-name in list view (to copy airtable styling)
# TODO Change/improve ui.label('Here is my list of priority : "Deadline", "Fire", "Priority", "Status"')
# TODO in todo list view, for todo-row change position of Fire icon, place it as a prefix of the todo row
# TODO correct deadline label format
# TODO ⚠️⚠️⚠️️ [if possible]to reduce size of script, create a single UI component which is "one️_todo_focus_window" that will be used for todo details showing and todo creation process


############# TITLE LIBRARIES AND MODULES #############
pass

from nicegui import app, ui
from collections import defaultdict
from typing import List, Dict, Callable
import database
import style
from constant import NOW_FR_DATE, STATUS_OPTIONS, PRIORITY_OPTIONS, SOURCE_OPTIONS, FIRE_OPTIONS

# Load the "Inter" font from Google Fonts for the whole page
ui.add_head_html('''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
    /* Apply the font to all elements that use it */
    body, .font-inter {
        font-family: 'Inter', sans-serif;
    }
</style>
''')

############# TITLE GLOBAL VARIABLES #############
list_view_groups_state = set()  # Records the state of the ui.expansion() elements in grouped list view
active_filters = {}  # Dictionary to store the user's selections made by selecting filters in the grouped list view


############# TITLE CLI FUNCTIONS #############

def group_todos_by_property(todos_list: list[dict], grouping_property: str) -> dict:
    """Groups a list of to-do dictionaries by their 'status' key.
        Details :
        - defaultdict(list) creates an empty dict
        - then for every todo, it will create a new key that is the provided grouping_property
        - it will insert a pair key (aka. "grouping_property") - value (aka. a list todos (dicts) sharing this grouping_property))
        - if the grouping_property already exists as a key inside grouped dict, then the todo will be insert as a new item
        - of the value-list linked to this existing key-grouping-property
    """
    grouped = defaultdict(list)
    for todo in todos_list:
        grouped[todo[f"{grouping_property}"]].append(todo)
    return grouped


############# TITLE LAYOUT FUNCTIONS #############
pass


# TODOS LIST VIEW (FILTER + NEW TO-DO)
def build_grouped_list_view(database_todos_list: list, property_used_for_grouping: str):
    """Creates an Airtable-like grouped list view."""
    grouped_todos = group_todos_by_property(todos_list=database_todos_list,
                                            grouping_property=property_used_for_grouping)

    global list_view_groups_state

    def update_groups_state(group_name: str):
        """Adds or removes the group name from the state set."""
        if group_name in list_view_groups_state:
            list_view_groups_state.discard(group_name)
        elif group_name not in list_view_groups_state:
            list_view_groups_state.add(group_name)

    # Loop through each group
    for group_name, todos in grouped_todos.items():

        # Check if group name is inside my list_view_groups_state set
        is_group_expanded = True if group_name in list_view_groups_state else False

        # Create a collapsible header for the group
        with ui.expansion(f'{group_name} ({len(todos)} items)', icon='drag_indicator', value=is_group_expanded).classes(
                'w-full') as group_header:
            # This column holds all the to-dos for this group
            ui.label('Here is my list of priority : "Deadline", "Fire", "Priority", "Status"')
            with ui.column().classes('w-full gap-0'):
                # Loop through each to-do in the current group
                for todo in todos:
                    # The main row for a single to-do item
                    with ui.row().classes('w-full p-3 items-center hover:bg-gray-50 cursor-pointer').on(
                            'click', lambda t=todo: open_todo_details(t)):
                        # To-do name (takes up all available space)
                        ui.label(todo['todo_name']).classes('flex-grow')

                        # Status "Pill"
                        status = todo["status"]
                        ui.label(status).classes(
                            f'w-28 text-center text-sm p-1 rounded-full {style.STATUS_COLORS.get(status, "bg-gray-200")}')

                        # Fire Icon
                        is_urgent = todo["fire_or_clock"]
                        ui.label('🔥' if is_urgent else '').classes('w-12 text-center text-xl')

                        # Priority "Pill"
                        priority = todo["priority"]
                        ui.label(priority).classes(
                            f'w-24 text-center text-sm p-1 rounded-full {style.PRIORITY_COLORS.get(priority, "bg-gray-200")}')

                        # Deadline
                        deadline = todo["deadline"]
                        ui.label(deadline).classes('w-32 text-right')

                    ui.separator()

        # .on() method is used to listen for an event (like a mouse click or a key press) on a UI element and run a function when that event happens.
        # 'update:model-value' tracks any changes of any type occuring on my UI element
        group_header.on('update:model-value',
                        lambda name=group_name: update_groups_state(group_name=name))


def build_filter_dropdown(name: str, options: List[str], filters: Dict):
    """Creates a robust, Airtable-style filter button with its own menu."""

    # This function defines the text logic
    def get_button_text(selections: List[str]) -> str:
        if not selections:
            return name
        elif len(selections) == 1:
            value_text = selections[0]
            return f'{name}: {value_text[:10] + "..." if len(value_text) > 10 else value_text}'
        else:
            return f'{name}: {len(selections)} selected'

    # Initialize the filter entry
    filters[name.lower()] = []

    # The button that will anchor the menu
    with ui.button() \
            .props('flat no-caps padding="4px 8px"') \
            .classes('bg-white hover:bg-gray-100 rounded-full shadow-sm border border-gray-300') as button:

        # The menu is now defined INSIDE the button's context
        with ui.menu():
            ui.label(f'Filter by {name}').classes('px-4 pt-2 font-semibold')
            ui.select(options, multiple=True) \
                .classes('w-56') \
                .bind_value(filters, name.lower()) \
                .on('update:model-value', lambda: (button.update(), ui.notify(f'Active filters: {filters}')))

        # The button's visual content (label and icon)
        with ui.row().classes('items-center gap-1'):
            ui.label().bind_text_from(filters, name.lower(), backward=get_button_text)
            ui.icon('expand_more', size='sm')


def build_filter_bar(filters: Dict):
    """Creates a horizontal bar of filter dropdowns."""
    with ui.row().classes('items-center gap-2 p-2'):
        ui.label('Filter by:').classes('text-gray-500')
        build_filter_dropdown('Status', STATUS_OPTIONS, filters)
        build_filter_dropdown('Priority', PRIORITY_OPTIONS, filters)
        build_filter_dropdown('Source', SOURCE_OPTIONS, filters)


def show_list_view(property_to_use_to_group: str):
    """
        Return the layout that will contain the main to-do list view (with filter bar) and to-do creation window.
        :return: list_view_page column element
    """
    global list_view_container

    all_database_todos: list = database.get_all_todos()

    with list_view_container:
        # Build the filter bar & "new todo" header
        with ui.row().classes('w-full justify-between items-center p-4 border-b'):
            # filter bar
            build_filter_bar(active_filters)
            # new-todo
            create_dialog = build_create_todo_dialog()  # The creation dialog will be invisible until opened.
            ui.button('New To-Do', icon='add', on_click=create_dialog.open).props('color=primary')

        # The grouped list of todos
        with ui.column().classes("w-full"):
            # Use the active current todos from SQL DB to display the list of todos, grouped by "source"
            build_grouped_list_view(database_todos_list=all_database_todos,
                                    property_used_for_grouping=property_to_use_to_group)

    # return list_view_container
    print("(1) show_list_view executed")


def refresh_list_view(property_to_use_to_group: str):
    global list_view_container
    list_view_container.clear()
    show_list_view(property_to_use_to_group=property_to_use_to_group)
    print("(2) refresh_list_view executed")


# SINGLE TO-DO FOCUS VIEW
def populate_todo_details_dialog_box(one_todo_from_database: dict):
    """Populates the todo_details_content_area element with the UI for a specific to-do."""
    global todo_details_content_area, todo_details_dialog
    # Clear any previous content
    todo_details_content_area.clear()

    # Build the UI inside the content area
    with todo_details_content_area:
        # The scroll area is now inside the content area
        with ui.scroll_area().classes('w-full h-full'):
            # HEADER SECTION
            with ui.row().classes("w-full no-wrap items-center p-2"):
                # Pass the actual to-do name to the input
                ui.input(value=one_todo_from_database['todo_name'],
                         on_change=lambda e: database.update_one_column(todo_id=one_todo_from_database["id"],
                                                                        column_to_update="todo_name",
                                                                        new_status=e.value)).classes(
                    style.AT_TODO_HEADER_STYLE).props("borderless")
                ui.button(text="Mark as done").classes(style.AT_DONE_BTN_STYLE).props('no-caps')

            # 1st SECTION : PRIORITY, STATUS, FIRE, SOURCE
            # Display this section as a row of 4 cells (grid element)
            with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
                with ui.grid(columns=4).classes("w-full p-2 !bg-[#f3f6fc]"):
                    # 1/4 : status
                    with ui.column():
                        ui.label("Status").classes(style.AT_TODO_PROPERTIES_HEADING)
                        ui.select(options=STATUS_OPTIONS,
                                  value=one_todo_from_database["status"]).classes(
                            style.AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')
                    # 2/4 : priority
                    with ui.column():
                        ui.label("Priorité").classes(style.AT_TODO_PROPERTIES_HEADING)
                        ui.select(options=PRIORITY_OPTIONS,
                                  value=one_todo_from_database["priority"]).classes(
                            style.AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')
                    # 3/4 : fire
                    with ui.column():
                        ui.label("Fire").classes(style.AT_TODO_PROPERTIES_HEADING)
                        ui.select(options=FIRE_OPTIONS,
                                  value=one_todo_from_database["fire_or_clock"]).classes(
                            style.AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')
                    # 4/4 : source
                    with ui.column():
                        ui.label("Source").classes(style.AT_TODO_PROPERTIES_HEADING)
                        ui.select(
                            options=SOURCE_OPTIONS, value=one_todo_from_database["source"]).classes(
                            style.AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')

            # 2nd SECTION : DEADLINE, CREATED TIME, LAST MODIFIED TIME
            # Display this section as a row of 3 cells (grid element)
            with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
                with ui.grid(columns=3).classes("w-full p-2 !bg-[#f3f6fc]"):
                    # 1/3 : deadline
                    with ui.column():
                        ui.label("Deadline").classes(style.AT_TODO_PROPERTIES_HEADING)
                        with ui.input().props("dense borderless").classes(style.AT_PROPERTY_SELECTOR_STYLE) as date:
                            with ui.menu().props('no-parent-event') as menu:
                                with ui.date().bind_value(date).props('mask="DD/MM/YYYY"'):
                                    with ui.row().classes('justify-end'):
                                        ui.button('Close', on_click=menu.close).props('flat')
                            with date.add_slot('append'):
                                ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                    # 2/3 : creation date
                    with ui.column():
                        ui.label("Created on").classes(style.AT_TODO_PROPERTIES_HEADING)
                        ui.label(text="12/03/2025").classes(style.AT_DATE_LABEL_STYLE).props(
                            'dense borderless')
                    # 2/3 : last modified time
                    with ui.column():
                        ui.label("Modified on").classes(
                            style.AT_TODO_PROPERTIES_HEADING)
                        ui.label(text="28/05/2025").classes(style.AT_DATE_LABEL_STYLE).props(
                            'dense borderless')

            # 3rd SECTION : COMMENTS & FILE ATTACHMENTS
            # Display this section as a row containing 2 columns
            with ui.row(wrap=False).classes("w-full p-2 !bg-[#f3f6fc]"):
                # 1/2 : comments section
                with ui.column().classes('w-[75%]'):
                    ui.label("Comments").classes(style.AT_TODO_PROPERTIES_HEADING)
                    ui.editor(placeholder='Type something here').classes("w-full")
                # 2/2 : file upload section
                with ui.column().classes('w-[25%]'):
                    ui.label("Attachments").classes(style.AT_TODO_PROPERTIES_HEADING)
                    ui.upload(
                        on_upload=lambda e: ui.notify(f'Uploaded {e.name}')).classes(
                        style.AT_UPLOAD_ZONE_STYLE).props(
                        'dense borderless')


def open_todo_details(todo: dict):
    """Clears, populates, and opens the details dialog for a given to-do."""
    global todo_details_dialog, todo_details_content_area
    populate_todo_details_dialog_box(todo)
    todo_details_dialog.open()
    print("open_todo_details successfully triggered")
    print(f"⚠️todo_details_dialog = {todo_details_dialog}")
    print(f"⚠️todo_details_content_area = {todo_details_content_area}")


# NEW TO-DO CREATION
def build_create_todo_dialog() -> ui.dialog:
    """Builds the 'Create To-Do' dialog window with its content."""

    with ui.dialog().props("full-width full-height") as dialog, ui.card().classes("w-full h-full"):
        with ui.column().classes('w-full h-full'):
            # HEADER SECTION
            with ui.row().classes("w-full no-wrap items-center p-2"):
                new_todo_name = ui.input(placeholder="Enter new to-do name...").classes(
                    style.AT_TODO_HEADER_STYLE).props("borderless")

                # This button will eventually save the new to-do
                ui.button("Create", on_click=lambda: (
                    ui.notify("To-do Created!"),
                    database.create_todo(todo_name=new_todo_name.value, status=status_dropdown_selector.value,
                                         priority=priority_dropdown_selector.value,
                                         fire_or_clock=fire_dropdown_selector.value,
                                         source=source_dropdown_selector.value,
                                         deadline=date.value, modified_time=modified_time_label.text,
                                         created_time=created_time_label.text,
                                         comments=comment_editor_property.value),
                    refresh_list_view(property_to_use_to_group="source"),
                    dialog.close()  # Close the dialog after creation
                )).classes(style.AT_CREATE_TODO_BTN_STYLE).props('no-caps')

            # CONTENT SECTION
            with ui.scroll_area().classes('w-full flex-grow p-4'):
                ui.label("Add properties for your new to-do below.")
                # 1st SECTION : PRIORITY, STATUS, FIRE, SOURCE
                # Display this section as a row of 4 cells (grid element)
                with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
                    with ui.grid(columns=4).classes("w-full p-2 !bg-[#f3f6fc]"):
                        # 1/4 : status
                        with ui.column():
                            ui.label("Status").classes(style.AT_TODO_PROPERTIES_HEADING)
                            status_dropdown_selector = ui.select(options=STATUS_OPTIONS, value="Todo").classes(
                                style.AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')
                        # 2/4 : priority
                        with ui.column():
                            ui.label("Priorité").classes(style.AT_TODO_PROPERTIES_HEADING)
                            priority_dropdown_selector = ui.select(options=PRIORITY_OPTIONS,
                                                                   value="High").classes(
                                style.AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')
                        # 3/4 : fire
                        with ui.column():
                            ui.label("Fire").classes(style.AT_TODO_PROPERTIES_HEADING)
                            fire_dropdown_selector = ui.select(options=FIRE_OPTIONS).classes(
                                style.AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')
                        # 4/4 : source
                        with ui.column():
                            ui.label("Source").classes(style.AT_TODO_PROPERTIES_HEADING)
                            source_dropdown_selector = ui.select(
                                options=SOURCE_OPTIONS).classes(
                                style.AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')

                # 2nd SECTION : DEADLINE, CREATED TIME, LAST MODIFIED TIME
                # Display this section as a row of 3 cells (grid element)
                with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
                    with ui.grid(columns=3).classes("w-full p-2 !bg-[#f3f6fc]"):
                        # 1/3 : deadline
                        with ui.column():
                            ui.label("Deadline").classes(style.AT_TODO_PROPERTIES_HEADING)
                            with ui.input().props("dense borderless").classes(style.AT_PROPERTY_SELECTOR_STYLE) as date:
                                with ui.menu().props('no-parent-event') as menu:
                                    with ui.date().bind_value(date):
                                        with ui.row().classes('justify-end'):
                                            ui.button('Close', on_click=menu.close).props('flat')
                                with date.add_slot('append'):
                                    ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                        # 2/3 : creation date, now by default
                        with ui.column():
                            ui.label("Created on").classes(style.AT_TODO_PROPERTIES_HEADING)
                            created_time_label = ui.label(text=f"{NOW_FR_DATE}").classes(
                                style.AT_DATE_LABEL_STYLE).props(
                                'dense borderless')
                        # 3/3 : last modified time, now by default
                        with ui.column():
                            ui.label("Modified on").classes(
                                style.AT_TODO_PROPERTIES_HEADING)
                            modified_time_label = ui.label(text=f"{NOW_FR_DATE}").classes(
                                style.AT_DATE_LABEL_STYLE).props(
                                'dense borderless')

                # 3rd SECTION : COMMENTS AND FILE ATTACHMENTS
                # Display this section as a row containing 2 columns
                with ui.row(wrap=False).classes("w-full p-2 !bg-[#f3f6fc]"):
                    # 1/2 : comments section
                    with ui.column().classes('w-[75%]'):
                        ui.label("Comments").classes(style.AT_TODO_PROPERTIES_HEADING)
                        comment_editor_property = ui.editor(placeholder='Type something here').classes("w-full")
                    # 2/2 : file upload section
                    with ui.column().classes('w-[25%]'):
                        ui.label("Attachments").classes(style.AT_TODO_PROPERTIES_HEADING)
                        ui.upload(
                            on_upload=lambda e: ui.notify(f'Uploaded {e.name}')).classes(
                            style.AT_UPLOAD_ZONE_STYLE).props(
                            'dense borderless')

    return dialog


############# TITLE MAIN LAYOUT LOGIC #############
pass

# GLOBAL VARIABLES FOR CONTAINER ELEMENTS
todo_details_dialog = None
todo_details_content_area = None
list_view_container = None

with ui.column().classes("w-full h-screen") as main_container:
    # Assign the created element to your global variable
    list_view_container = ui.column().classes("w-full h-screen")

    # Build the initial list view inside the container
    show_list_view(property_to_use_to_group="source")

    # Build the TO-DO DETAILS DIALOG BOX hidden for the moment and assign it to the global variable
    with ui.dialog().props('full-width full-height').on('escape-key',
                                                        lambda: (
                                                                refresh_list_view(
                                                                    property_to_use_to_group="source"),
                                                                todo_details_dialog.close())) as local_scope_dialog:
        # Assign the created dialog to my global variable
        todo_details_dialog = local_scope_dialog
        with ui.card().classes("w-full h-full"):
            # Assign the created column to your global variable
            todo_details_content_area = ui.column().classes('w-full h-full')

# Testing
ui.run(language='fr')
