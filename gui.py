############# TODO LIST
# Logic / interactions
# Write full comments and docstrings for my FILE MANAGEMENT functions

# Others
# 1) Make the filtering work
# 2) Add a search box tool
# 3) Add a sort functionnality
# 3) Add an other "grouping" complex function to group with desired source


############# TITLE LIBRARIES AND MODULES #############
pass

from nicegui import ui, events
from nicegui.events import UploadEventArguments
from collections import defaultdict  # To create an empty dict that can be filled with [keys]-[list_values]
from typing import List, Dict, Optional
import database  # My file that manages sql queries
import style  # My file that manages some specific redundant styling used in gui
from constant import STATUS_OPTIONS, PRIORITY_OPTIONS, SOURCE_OPTIONS, FIRE_OPTIONS
import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import secrets
import string

style.GOOGLE_INTER_FONT  # Load the "Inter" font for the whole page

############# TITLE GLOBAL VARIABLES #############
list_view_groups_state = set()  # Records the state of the ui.expansion() elements in grouped_list_view
active_filters = {}  # Stores user's selections when selecting filters in the grouped_list_view
list_view_container = None  # Contains the grouped_list_view layout built with build_list_page()
UPLOADS_DIR = Path("/Users/sevakkulinkian/Documents/Todo_app_saved_files")
active_upload_dir = None  # Holds the state for the current, in-progress upload operation
upload_progress: dict = {"total": 0,
                         "completed": 0}  # Tracks the progress of a multi-file upload batch ('total' vs. 'completed').
upload_batch_data: list = []

############# TITLE LAYOUT FUNCTIONS #############
pass


# ----MISCELLANEOUS FUNCTIONS----
@ui.refreshable
def get_fresh_fr_date_with_time() -> str:
    """Gets current time in France and formats it as a string.
    Returns:
        str: The current date and time in "DD/MM/YYYY HH:MM" format.
    """
    # Get the current time in UTC (as you did)
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    # Convert it to the French timezone (Europe/Paris)
    french_timezone = ZoneInfo("Europe/Paris")
    now_french = now_utc.astimezone(french_timezone)
    # Format the result into your desired string format
    formatted_fr_date_time = now_french.strftime("%d/%m/%Y %H:%M")
    return formatted_fr_date_time


# ----FILES UPLOAD MANAGEMENT----
def generate_short_id(length_desired: int) -> str:
    """Generates a short and URL-safe random ID.
        Args:
            length_desired: The desired length of the generated ID string.
        Returns:
            A random string of the specified length containing letters and digits.
    """
    auth_characters = string.ascii_letters + string.digits
    unique_id: str = "".join(secrets.choice(auth_characters) for _ in range(length_desired))
    return unique_id


def format_unique_id_folder_name(current_todo_name=str, max_len: int = 85, unique_id=generate_short_id(8)) -> Dict[
    str, str]:
    """Formats a to-do name into a safe and unique directory name.

        Sanitizes a given string by replacing spaces with underscores and converting it to lowercase. Then truncates
        the name to a maximum length and prepends a unique ID to prevent naming conflicts.

        Args:
            current_todo_name: The original name of the to-do.
            max_len: The maximum length of the sanitized name part.
            unique_id: The unique identifier to prepend to the name.

        Returns:
            A dictionary containing two formatted versions of the name:
            - 'no_space': The sanitized and truncated name.
            - 'unique_title': The final, unique folder name string.
    """
    no_space_name: str = current_todo_name.replace(" ", "_").lower()
    truncated_version: str = no_space_name[:max_len]
    file_formatted_title_dict: dict = dict(no_space=no_space_name, unique_title=f"{unique_id}_{truncated_version}")
    return file_formatted_title_dict


def find_todo_dir(no_space_todo_name: str) -> Optional[str]:
    """Searches for an existing directory associated with a to-do.

        This function iterates through subdirectories in the global 'UPLOADS_DIR' and returns the full name of the first
        directory that contains the provided sanitized to-do name.

        Args:
            no_space_todo_name: The sanitized (lowercase, no spaces) name of the
                                to-do to search for.

        Returns:
            The full name of the matching folder if found, otherwise None.
    """
    global UPLOADS_DIR
    # Create list of all current folders that are inside main_folder
    subfolder_names: list = [item.name for item in UPLOADS_DIR.iterdir() if item.is_dir()]
    # Loop through all items in the parent directory
    for folder_name in subfolder_names:
        # Check if the item contains our to-do name
        if no_space_todo_name in folder_name:
            # If we find a match, return its name immediately
            return folder_name
    # If the loop finishes without finding any match, return None
    return None


def prepare_upload_destination(e: events.GenericEventArguments, clicked_todo: dict) -> Path:
    """Handles the file 'added' event to prepare a directory for an upload batch.

       Use only for "Edit" mode.

       This function is triggered once when a user selects one or more files in a ui.upload element. It checks if
       a directory for the associated to-do already exists. If not, it creates a new unique directory. It also resets the
       global upload progress counter.

       Finally, it stores and returns the absolute path of the target directory
       for the subsequent 'on_upload' events to use.

       Args:
           e: The event arguments from the 'added' event, containing the list of files.
           clicked_todo: The dictionary of the to-do item to which files are being added.

       Returns:
           A pathlib.Path object representing the absolute path to the target
           directory for the upload batch.
       """
    global UPLOADS_DIR, active_upload_dir, upload_progress
    clicked_todo_name: str = clicked_todo["todo_name"]
    no_space_formatted_name: str = format_unique_id_folder_name(current_todo_name=clicked_todo_name)["no_space"]
    # Reset the global scope counter every time a batch of files is placed into the ui.upload element
    upload_progress["total"] = len(e.args)
    upload_progress["completed"] = 0
    # Look for an existing folder attached to that todo, and returns str folder's name if one exists, else returns None
    folder_attached_to_todo: str = find_todo_dir(no_space_todo_name=no_space_formatted_name)

    # If no folder attached to the clicked todo has been found, creates a new one, formatted the correct way
    if not folder_attached_to_todo:
        unique_folder_name: str = format_unique_id_folder_name(current_todo_name=clicked_todo["todo_name"])[
            "unique_title"]
        new_folder_abs_path = Path(f"{UPLOADS_DIR}/{unique_folder_name}")
        new_folder_abs_path.mkdir()  # Creates the folder
        active_upload_dir = new_folder_abs_path  # Stores target directory's abs path for next 'on_upload' events to use
        return active_upload_dir
    # If a folder attached to that todo already exists, returns its abs path
    else:
        existing_folder_abs_path: str = Path(f"{UPLOADS_DIR}/{folder_attached_to_todo}")
        active_upload_dir = existing_folder_abs_path  # Stores target directory's abs path for next 'on_upload' events to use
        return active_upload_dir


def save_uploaded_file(e: UploadEventArguments):
    """Handles the upload of a single file as part of a batch.

        Use only for "Edit" mode.

        This function is triggered by the 'on_upload' event for each file. It saves the received file to a pre-determined
        directory (stored in a global variable), increments a global progress counter, and checks if all files in the
        current batch have been successfully uploaded.

        If X files are uploaded, then this function will be triggered X times until end.

        Args:
            e: The event arguments from the 'on_upload' event, containing the
               name and content of the single uploaded file.
    """
    global active_upload_dir, upload_progress

    # Save ONE file at a time
    file_abs_path: str = f"{active_upload_dir}/{e.name.replace(" ", "_")}"
    with open(file_abs_path, "wb") as f:
        f.write(e.content.read())

    # Increment the global scope counter (that was reset by previous prepare_upload_destination function)
    upload_progress["completed"] += 1

    # Check if the batch is now complete to stop the process by a final closing step triggered if only condition is met
    # (eg : print and database update)
    if upload_progress["total"] == upload_progress["completed"]:
        print("All files have been uploaded!")
        # TODO Here I can update my database to store the abs_path of my todo_folder or any other best practice with SQLite


def save_upload_batch_data(e: UploadEventArguments):
    """
        Collects individual file data into a temporary list for a new to-do that are stored as dict inside the list.

        Use only for "Create" mode.

        This function is used as the 'on_upload' handler in "create" mode. It is
        called for each successfully uploaded file, where it extracts the file's
        content and name, and appends them to the global 'upload_batch_data'
        list for processing later when the "Create" button is clicked.

        Args:
            e: The event arguments for a single file upload, containing its
               name and content.
    """
    global upload_batch_data
    file_data: dict = {"file_content": e.content, "file_name": e.name, "file_formatted_name": e.name.replace(" ", "_")}
    upload_batch_data.append(file_data)


def handle_upload_files_create_mode(files_data_list: list, created_todo_name: str):
    """
        Creates a new directory and saves a batch of uploaded files into it.

        Use only for "Create" mode.

        This function is called after a new to-do has been named. It generates a
        unique folder name based on the to-do's name, creates the corresponding
        directory, and then iterates through a list of pre-collected file data
        to save each file to the new directory.

        Args:
            files_data_list: A list of dictionaries, where each dictionary
                             contains the content and name of a file to be saved.
            created_todo_name: The final name of the new to-do, used to
                               generate the directory name.
    """
    global UPLOADS_DIR
    new_folder_name: str = format_unique_id_folder_name(current_todo_name=created_todo_name)["unique_title"]
    folder_abs_path: Path = Path(f"{UPLOADS_DIR}/{new_folder_name}")
    folder_abs_path.mkdir()
    for file_data in files_data_list:
        file_abs_path: str = f"{folder_abs_path}/{file_data["file_formatted_name"]}"
        with open(file_abs_path, "wb") as f:
            f.write(file_data["file_content"].read())


# ----GROUPED LIST PAGE AND ITS ELEMENTS----
def build_filter_button(name: str, options: List[str], filters: Dict):
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


def build_filter_bar(filters: dict):
    """Creates a horizontal bar of filter dropdowns."""
    with ui.row().classes('items-center gap-2 p-2'):
        # ui.label('Filter by').classes('px-4 font-semibold text-white text-base')
        build_filter_button('Status', STATUS_OPTIONS, filters)
        build_filter_button('Priority', PRIORITY_OPTIONS, filters)
        build_filter_button('Source', SOURCE_OPTIONS, filters)
        build_filter_button('Fire', FIRE_OPTIONS, filters)


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


def build_grouped_list(database_todos_list: list, property_used_for_grouping: str):
    """Creates an Airtable-like grouped list view.
        Headers (= grouping_property) can expand and show rows (= todos under the group)
    """
    # This set() variable will save which group.s are expanded (or not) in order to find back our list view
    # as it was once we leave a to-do single window we
    global list_view_groups_state

    def update_groups_state(group_name: str):
        """Adds or removes the group name from the list_view_groups_state set().
            This function will be triggered every time there is a change occuring on the header of any group
            thanks to .on('update:model-value',...) at the end of build_grouped_list function
        """
        if group_name in list_view_groups_state:
            list_view_groups_state.discard(group_name)
        elif group_name not in list_view_groups_state:
            list_view_groups_state.add(group_name)

    # Creates a dict where keys are str (=grouping_property) and values are list of todos-dict
    grouped_todos = group_todos_by_property(todos_list=database_todos_list,
                                            grouping_property=property_used_for_grouping)
    # Loop through each group
    for group_name, todos_in_group in grouped_todos.items():

        # Check if group name is inside my list_view_groups_state set
        is_group_expanded = True if group_name in list_view_groups_state else False

        # Create a collapsible header for the group
        with ui.expansion(
                value=is_group_expanded).props("switch-toggle-side").classes(
            'w-full text-lg') as group_header:
            # Customize visually the header of the group with add_slot
            with group_header.add_slot("header"):
                with ui.row().classes("items-center"):
                    ui.label(f'{group_name}').classes("bg-gray-200 rounded px-2 py-1")
                    ui.label(f'{len(todos_in_group)}').classes("ml-1 text-gray-500")

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
                for todo in todos_in_group:
                    # A row = a single to-do item
                    with ui.row().classes('w-full p-3 items-center hover:bg-gray-50 cursor-pointer text-lg').on(
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
                        lambda name=group_name: update_groups_state(group_name=name))


def build_list_page(property_to_use_to_group: str):
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
            build_filter_bar(active_filters)
            # new-todo
            todo_creation_dialog_box = build_create_todo_dialog()  # The creation dialog will be invisible until opened.
            ui.button('Create new todo', on_click=todo_creation_dialog_box.open).classes(
                "bg-black rounded text-white font-semibold px-4 py-2 text-lg").props("no-caps")

        # The grouped list of todos
        with ui.column().classes("w-full"):
            # Use the active current todos from SQL DB to display the list of todos, grouped by "source"
            build_grouped_list(database_todos_list=all_database_todos,
                               property_used_for_grouping=property_to_use_to_group)


def refresh_list_view(property_to_use_to_group: str):
    """When triggered by pressing on the top-right corner CTA of a single focus todo window, this function
    cleans up and build again the group list view that appears in the global scope var list_view_container.
    """
    global list_view_container
    list_view_container.clear()
    build_list_page(property_to_use_to_group=property_to_use_to_group)


# ----SINGLE TO-DO WINDOW AND ITS ELEMENTS----

# TODO Fix the "deadline" problem thanks to Gemini answer


def build_todo_view(todo_data: dict, usage_type: str) -> ui.column:
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
    global upload_batch_data
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
                                                      deadline=date.value,
                                                      modified_time=f"{get_fresh_fr_date_with_time()}",
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
                        handle_upload_files_create_mode(files_data_list=upload_batch_data,
                                                        created_todo_name=todo_name.value),
                        refresh_list_view(property_to_use_to_group="source")
                    )).classes(style.AT_DONE_CTA_BTN_STYLE).props('no-caps')
                    return generic_btn

                else:
                    print("Error")

            # Create the CTA button
            build_cta_btn()

            # TODO add feature to delete also the directory and files attached to the todo
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

                    def populate_creation_date_field() -> ui.button:
                        """Dynamically creates the creation date for todo in 'Create' mode.
                            Returns: ui.button
                        """
                        if usage_type == "create":
                            initial_created_time = ui.label(text=f"{get_fresh_fr_date_with_time()}").classes(
                                style.AT_DATE_LABEL_STYLE).props(
                                'dense borderless')
                            return initial_created_time
                        elif usage_type == "edit":
                            created_time_from_database = ui.label(text=f"{todo_data["created_time"]}").classes(
                                style.AT_DATE_LABEL_STYLE).props(
                                'dense borderless')
                            return created_time_from_database

                    created_time_label = populate_creation_date_field()

                # 2/3 : last modified time
                with ui.column():
                    ui.label("Modified on").classes(
                        style.AT_TODO_PROPERTIES_HEADING)
                    modified_time_label = ui.label(text=f"{todo_data["modified_time"]}").classes(
                        style.AT_DATE_LABEL_STYLE).props(
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
                # "Edit mode" file upload management
                if usage_type == "edit":
                    ui.upload(
                        on_upload=lambda e: save_uploaded_file(e), multiple=True).on(
                        "added", lambda e: prepare_upload_destination(e, clicked_todo=todo_data)).classes(
                        style.AT_UPLOAD_ZONE_STYLE).props(
                        'dense borderless')
                # "Create mode" file upload management
                if usage_type == "create":
                    ui.label("Create mode")
                    ui.upload(
                        on_upload=lambda e: save_upload_batch_data(e), multiple=True).classes(
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
        "created_time": f"{get_fresh_fr_date_with_time()}",
        "comments": ""
    }
    with ui.dialog().props("full-width full-height") as todo_creation_dialog:
        build_todo_view(todo_data=empty_todo_dict, usage_type="create")
        return todo_creation_dialog


def build_details_dialog(todo_to_display: dict) -> ui.dialog:
    """Builds the 'Todo details" dialog window with its content."""
    with ui.dialog().props("full-width full-height") as todo_details_dialog:
        build_todo_view(todo_data=todo_to_display, usage_type="edit")
        return todo_details_dialog


def open_todo_details(todo: dict):
    """Builds and displays the details dialog for a specific to-do.

        This function is triggered when a to-do item is clicked, cf. build_grouped_list() function.
        It takes a to-do's data, passes it to a builder function to construct
        the details dialog (build_details_dialog), and then opens the dialog on the screen.

        Args:
            todo: A dictionary containing the data for the selected to-do.
        """
    todo_details_dialog = build_details_dialog(todo_to_display=todo)
    todo_details_dialog.open()


############# TITLE MAIN LAYOUT LOGIC #############
pass

with ui.column().classes("w-full h-screen") as main_container:
    # Assign the created element to your global variable
    list_view_container = ui.column().classes("w-full h-screen")

    # Build the initial list view inside that list_view_container
    build_list_page(property_to_use_to_group="source")

# ----APP RUNNING----
ui.run(language='fr')
