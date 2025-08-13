############# TODO LIST
# Logic / interactions
# 1) Make the filtering work


############# TITLE LIBRARIES AND MODULES #############
pass

from nicegui import app, ui
from collections import defaultdict
from typing import List, Dict, Callable
import database
import style
from constant import NOW_FR_DATE, STATUS_OPTIONS, PRIORITY_OPTIONS, SOURCE_OPTIONS, FIRE_OPTIONS

style.GOOGLE_INTER_FONT  # Load the "Inter" font for the whole page

############# TITLE GLOBAL VARIABLES #############
list_view_groups_state = set()  # Records the state of the ui.expansion() elements in grouped_list_view
active_filters = {}  # Stores user's selections when selecting filters in the grouped_list_view
list_view_container = None  # Contains the grouped_list_view layout built with show_list_view()

############# TITLE LAYOUT FUNCTIONS #############
pass


# ABOUT THE LIST VIEW AND ITS ELEMENTS

def build_filter_dropdown_btn_element(name: str, options: List[str], filters: Dict):
    """Creates an Airtable-style filter button with its own menu."""

    def get_button_text(selections: List[str]) -> str:
        """Defines the text appearing inside the filtering dropdown button when selection is made"""
        if not selections:
            return name
        elif len(selections) == 1:
            value_text = selections[0]
            return f'{name}: {value_text[:10] + "..." if len(value_text) > 10 else value_text}'
        else:
            return f'{name}: {len(selections)} selected'

    def active_filters_notification_msg(active_filters: dict) -> str:
        """Builds a nice sentence that will be displayed each time a filter option is (un)selected"""
        sentence_items = []

        for property, list_of_selections in active_filters.items():
            filter_not_empty = True if len(list_of_selections) > 0 else False
            if filter_not_empty:
                for selection in list_of_selections:
                    sentence_items.append(f"{selection}")

        joined_str_items: str = "  │  ".join(sentence_items)
        formatted_sentence: str = f"Active filters : {joined_str_items}."
        return formatted_sentence

    # Initialize the filter entry
    filters[name.lower()] = []

    # The button that will anchor the menu
    airtable_shadow = 'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
    with ui.button() \
            .props('flat no-caps') \
            .classes(
        f'bg-white hover:bg-gray-100 rounded-md text-zinc-900 text-[13px] {airtable_shadow} mr-2 px-[6px] py-[4px]') as button:

        # The menu is now defined INSIDE the button's context
        with ui.menu():
            ui.label(f'Filter by {name}').classes('px-4 pt-2 font-semibold')
            ui.select(options, multiple=True) \
                .classes('w-56') \
                .bind_value(filters, name.lower()) \
                .on('update:model-value',
                    lambda: (button.update(), ui.notify(f'{active_filters_notification_msg(active_filters)}')))

        # The button's visual content (label and icon)
        with ui.row().classes('items-center gap-2 no-wrap'):
            ui.label().bind_text_from(filters, name.lower(), backward=get_button_text).classes(
                "truncate text-black font-light text-lg")
            ui.icon('expand_more', size='sm').classes("text-black font-thin")


def build_filter_bar_save_choices(filters: dict):
    """Creates a horizontal bar of filter dropdowns."""
    with ui.row().classes('items-center gap-2 p-2'):
        # ui.label('Filter by').classes('px-4 font-semibold text-white text-base')
        build_filter_dropdown_btn_element('Status', STATUS_OPTIONS, filters)
        build_filter_dropdown_btn_element('Priority', PRIORITY_OPTIONS, filters)
        build_filter_dropdown_btn_element('Source', SOURCE_OPTIONS, filters)
        build_filter_dropdown_btn_element('Fire', FIRE_OPTIONS, filters)


def group_todos_by_property(todos_list: list[dict], grouping_property: str) -> dict:
    """Reorganizes a flat list of to-dos into a dictionary of groups.
        Details :
        1. defaultdict(list) creates an empty dict that can be filled with key-list_value
        2. for every todo (loop), if needed, a new key is created that corresponds to the provided grouping_property
        (if the grouping_property already exists as a key inside grouped dict, then go step 3.)
        3. it sticks the todo (dict) inside the value-list linked to the correct key/grouping_property
        4. returns a dict (key = grouping_property) of list of dicts [todos]
    """
    grouped = defaultdict(list)
    for todo in todos_list:
        grouped[todo[f"{grouping_property}"]].append(todo)
    return grouped


def build_grouped_list_view(database_todos_list: list, property_used_for_grouping: str):
    """Creates an Airtable-like grouped list view.
        Headers (= grouping_property) can expand and show rows (= todos under the group)
    """
    # This set() variable will save which group.s are expanded (or not) in order to find back our list view
    # as it was once we leave a to-do single window we
    global list_view_groups_state

    def update_groups_state(group_name: str):
        """Adds or removes the group name from the list_view_groups_state set().
            This function will be triggered every time there is a change occuring on the header of any group
            thanks to .on('update:model-value',...) at the end of build_grouped_list_view function
        """
        if group_name in list_view_groups_state:
            list_view_groups_state.discard(group_name)
        elif group_name not in list_view_groups_state:
            list_view_groups_state.add(group_name)

    # Creates a dict where keys are str (=grouping_property) and values are list of todos-dict
    grouped_todos = group_todos_by_property(todos_list=database_todos_list,
                                            grouping_property=property_used_for_grouping)
    # Loop through each group
    for group_header_name, list_of_todos in grouped_todos.items():

        # Check if group name is inside my list_view_groups_state set
        is_group_expanded = True if group_header_name in list_view_groups_state else False

        # Create a collapsible header for the group
        with ui.expansion(
                value=is_group_expanded).props("switch-toggle-side").classes(
            'w-full text-lg') as group_header:
            # Customize visually the header of the group with add_slot
            with group_header.add_slot("header"):
                with ui.row().classes("items-center"):
                    ui.label(f'{group_header_name}').classes("bg-gray-200 rounded px-2 py-1")
                    ui.label(f'{len(list_of_todos)}').classes("ml-1 text-gray-500")

            # This column holds all the todos of the group
            with ui.column().classes('w-full gap-0'):
                # Mini header row on top of the todos inside the group
                with ui.row().classes('w-full px-2 py-0 items-center text-sm text-gray-500 font-normal'):
                    # This empty label acts as a spacer to align with the to-do names, by taking all the available space
                    ui.label().classes('flex-grow')
                    # Add labels for each column, matching the widths of the data below
                    ui.label('Status').classes('w-28 text-center')
                    ui.label('Priority').classes('w-24 text-center')
                    ui.label('Deadline').classes('w-32 text-center')

                # Loop through each todo in the current group (and its todos list)
                for todo in list_of_todos:
                    # A row = a single to-do item
                    with ui.row().classes('w-full p-3 items-center hover:bg-gray-50 cursor-pointer text-base').on(
                            'click', lambda t=todo: open_todo_details(t)):
                        # Fire icon
                        fire_icon_to_display: str = "" if todo["fire_or_clock"] == None else todo["fire_or_clock"]
                        ui.label(text=f"{fire_icon_to_display}").classes('w-12 text-center text-xl')

                        # To-do name (takes up all available space)
                        ui.label(todo['todo_name']).classes('flex-grow')

                        # Status pill
                        status = todo["status"]
                        ui.label(status).classes(
                            f'w-28 text-center text-sm p-1 rounded-full {style.STATUS_COLORS.get(status, "bg-gray-200")}')

                        # Priority pill
                        priority = todo["priority"]
                        ui.label(priority).classes(
                            f'w-24 text-center text-sm p-1 rounded-full {style.PRIORITY_COLORS.get(priority, "bg-gray-200")}')

                        # Deadline
                        deadline = todo["deadline"]
                        ui.label(deadline).classes('w-32 text-center')

                    ui.separator()

        # .on() method is used to listen for an event (like a mouse click or a key press) on a UI element
        # then it runs a function when that event happens.
        # 'update:model-value' tracks any changes of any type occurring on my UI element
        group_header.on('update:model-value',
                        lambda name=group_header_name: update_groups_state(group_name=name))


def show_list_view(property_to_use_to_group: str):
    """
        Return the layout that will contain the main to-do list view (with filter bar) and to-do creation window.
        :return: list_view_page column element
    """
    global list_view_container  # Permanent variable at end of script to store this view

    all_database_todos: list = database.get_all_todos()

    with list_view_container:
        # Build the filter bar & "new todo" header
        with ui.row().classes('w-full justify-between items-center p-4 border-b bg-white'):
            # filter bar
            build_filter_bar_save_choices(active_filters)
            # new-todo
            todo_creation_dialog_box = build_create_todo_dialog()  # The creation dialog will be invisible until opened.
            ui.button('Create new todo',  on_click=todo_creation_dialog_box.open).classes(
                "bg-black rounded text-white font-semibold px-4 py-2 text-lg").props("no-caps")

        # The grouped list of todos
        with ui.column().classes("w-full"):
            # Use the active current todos from SQL DB to display the list of todos, grouped by "source"
            build_grouped_list_view(database_todos_list=all_database_todos,
                                    property_used_for_grouping=property_to_use_to_group)


def refresh_list_view(property_to_use_to_group: str):
    """When triggered by pressing on the top-right corner CTA of a single focus todo window, this function
    cleans up and build again the group list view that appears in the global scope var list_view_container.
    """
    global list_view_container
    list_view_container.clear()
    show_list_view(property_to_use_to_group=property_to_use_to_group)


# ABOUT SINGLE TO-DO WINDOW AND ITS ELEMENTS
def build_todo_window_shared_layout(todo_data: dict, usage_type: str) -> ui.column:
    """Builds the shared UI form for creating or editing a to-do item.

        This function acts as a reusable component that generates the entire layout
        for a focused to-do view, including header, properties, and comments sections.
        It adapts its behavior based on the specified usage type ('create' or 'edit').

        Args:
            todo_data: A dictionary containing the data for a to-do.
                       - For 'edit' mode, this should be a full dictionary from the database.
                       - For 'create' mode, this can be a dictionary with default values.
            usage_type: A string that determines the component's mode ('create' or 'edit').
                        This controls which action button (or CTA) is displayed (at the top-right corner of the window) and its behavior.

        Returns:
            The `ui.column` element containing the entire shared layout.
        """
    with ui.column().classes('w-full h-full bg-white p-4') as shared_one_todo_focus_layout:

        # HEADER SECTION (to-do name + CTA)
        with ui.row().classes("w-full no-wrap items-center p-2"):

            # To-do name
            todo_name = ui.input(value=todo_data['todo_name']).classes(style.AT_TODO_HEADER_STYLE).props(
                "borderless")

            # Generates adequate CTA btn depending on edit or create usecase
            def build_cta_btn() -> ui.button:
                """Dynamically creates and returns either an 'Edit' or 'Create' button.
                    Returns: ui.button
                """
                if usage_type == "edit":
                    generic_btn = ui.button(text="Edit", on_click=lambda: (
                        database.update_todo_entirely(todo_id=todo_data["id"], todo_name=todo_name.value,
                                                      status=status_dropdown_selector.value,
                                                      priority=priority_dropdown_selector.value,
                                                      fire_or_clock=fire_dropdown_selector.value,
                                                      source=source_dropdown_selector.value,
                                                      deadline=date.value, modified_time=modified_time_label.text,
                                                      created_time=created_time_label.text,
                                                      comments=comment_editor_property.value),
                        ui.notify("✅ Todo edited!"),
                        refresh_list_view(property_to_use_to_group="source"))).classes(
                        style.AT_DONE_CTA_BTN_STYLE).props('no-caps')
                    return generic_btn

                elif usage_type == "create":
                    generic_btn = ui.button(text="Create", on_click=lambda: (
                        ui.notify("✅ Todo created!"),
                        database.create_todo(todo_name=todo_name.value, status=status_dropdown_selector.value,
                                             priority=priority_dropdown_selector.value,
                                             fire_or_clock=fire_dropdown_selector.value,
                                             source=source_dropdown_selector.value,
                                             deadline=date.value, modified_time=modified_time_label.text,
                                             created_time=created_time_label.text,
                                             comments=comment_editor_property.value),
                        refresh_list_view(property_to_use_to_group="source")
                    )).classes(style.AT_DONE_CTA_BTN_STYLE).props('no-caps')
                    return generic_btn

                else:
                    print("Error")

            # Create the CTA button
            action_btn = build_cta_btn()

            def build_delete_todo_btn() -> ui.button:
                """Dynamically creates a "delete button" for todo in 'Edit' mode.
                    Returns: ui.button
                """
                if usage_type == "edit":
                    delete_btn = ui.button(text="Delete",
                                           on_click=lambda: (ui.notify(message="✅ Todo deleted from database!"),
                                                             database.delete_todo(
                                                                 todo_id=todo_data["id"]),
                                                             refresh_list_view(
                                                                 property_to_use_to_group="source"),
                                                             )).classes(
                        style.AT_DONE_DELETE_BTN_STYLE).props('no-caps')
                    return delete_btn

            # Create the delete button
            delete_btn_edit_mode = build_delete_todo_btn()

        # 1st SECTION (4 cells grid element in a row) : PRIORITY, STATUS, FIRE, SOURCE
        with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
            with ui.grid(columns=4).classes("w-full p-2 !bg-[#f3f6fc]"):
                # 1/4 : status
                with ui.column():
                    ui.label("Status").classes(style.AT_TODO_PROPERTIES_HEADING)
                    status_dropdown_selector = ui.select(options=STATUS_OPTIONS,
                                                         value=todo_data["status"]).classes(
                        style.AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')
                # 2/4 : priority
                with ui.column():
                    ui.label("Priorité").classes(style.AT_TODO_PROPERTIES_HEADING)
                    priority_dropdown_selector = ui.select(options=PRIORITY_OPTIONS,
                                                           value=todo_data["priority"]).classes(
                        style.AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')
                # 3/4 : fire
                with ui.column():
                    ui.label("Fire").classes(style.AT_TODO_PROPERTIES_HEADING)
                    fire_dropdown_selector = ui.select(options=FIRE_OPTIONS,
                                                       value=todo_data["fire_or_clock"]).classes(
                        style.AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')
                # 4/4 : source
                with ui.column():
                    ui.label("Source").classes(style.AT_TODO_PROPERTIES_HEADING)
                    source_dropdown_selector = ui.select(
                        options=SOURCE_OPTIONS, value=todo_data["source"]).classes(
                        style.AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')

        # 2nd SECTION (3 cells grid element in a row) : DEADLINE, CREATED TIME, LAST MODIFIED TIME
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
                    created_time_label = ui.label(text="12/03/2025").classes(style.AT_DATE_LABEL_STYLE).props(
                        'dense borderless')
                # 2/3 : last modified time
                with ui.column():
                    ui.label("Modified on").classes(
                        style.AT_TODO_PROPERTIES_HEADING)
                    modified_time_label = ui.label(text="28/05/2025").classes(style.AT_DATE_LABEL_STYLE).props(
                        'dense borderless')

        # 3rd SECTION (2 cols in a row) : COMMENTS & FILE ATTACHMENTS
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

    # Return the ui.column() containing all
    return shared_one_todo_focus_layout


def build_create_todo_dialog() -> ui.dialog:
    """Builds the 'Create Todo" dialog window with its content."""

    empty_todo_dict: dict = {
        "todo_name": "Enter new to-do name...",
        "status": "Todo",
        "priority": "High",
        "fire_or_clock": "",
        "source": "🔒 Perso",
        "deadline": "",
        "modified_time": "",
        "created_time": f"{NOW_FR_DATE}",
        "comments": ""
    }
    with ui.dialog().props("full-width full-height") as todo_creation_dialog:
        build_todo_window_shared_layout(todo_data=empty_todo_dict, usage_type="create")
        return todo_creation_dialog


def build_todos_details_dialog(todo_to_display: dict) -> ui.dialog:
    """Builds the 'Todo details" dialog window with its content."""
    with ui.dialog().props("full-width full-height") as todo_details_dialog:
        build_todo_window_shared_layout(todo_data=todo_to_display, usage_type="edit")
        return todo_details_dialog


def open_todo_details(todo: dict):
    """Builds and displays the details dialog for a specific to-do.

        This function is triggered when a to-do item is clicked, cf. build_grouped_list_view() function.
        It takes a to-do's data, passes it to a builder function to construct
        the details dialog (build_todos_details_dialog), and then opens the dialog on the screen.

        Args:
            todo: A dictionary containing the data for the selected to-do.
        """
    todo_details_dialog = build_todos_details_dialog(todo_to_display=todo)
    todo_details_dialog.open()


############# TITLE MAIN LAYOUT LOGIC #############
pass

with ui.column().classes("w-full h-screen") as main_container:
    # Assign the created element to your global variable
    list_view_container = ui.column().classes("w-full h-screen")

    # Build the initial list view inside that list_view_container
    show_list_view(property_to_use_to_group="source")

# Testing
ui.run(language='fr')
