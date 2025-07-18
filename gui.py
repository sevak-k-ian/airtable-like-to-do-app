# TODO Allew the todo details dialog box to be wider and bigger

############# TITLE LIBRARIES AND MODULES #############
pass
from nicegui import app, ui
import datetime
# Get current time to generate realistic timestamps
from zoneinfo import ZoneInfo
from collections import defaultdict
from typing import List, Dict, Callable


############# TITLE CONSTANT AND GLOBAL VARIABLES #############
pass
# 1. Get the current time in UTC (as you did)
now_utc = datetime.datetime.now(datetime.timezone.utc)
# 2. Convert it to the French timezone (Europe/Paris)
french_timezone = ZoneInfo("Europe/Paris")
now_french = now_utc.astimezone(french_timezone)
# 3. Format the result into your desired string format
FORMATTED_FR_DATE = now_french.strftime("%d/%m/%Y %H:%M")

# Properties and their available values
STATUS_OPTIONS = ["Todo", "Done"]
PRIORITY_OPTIONS = ["High", "Medium", "Low"]
SOURCE_OPTIONS = ["🔒 Perso", "👩‍❤️‍👨 Famille", "👶 Yeraz", "🤱 Mama", "💼 Hameaux Légers"]
FIRE_OPTIONS = ["🔥", "⏰", ""]


############# TITLE DUMMY DICT AND DATA FOR TESTING #############
pass
todos_sample = [
    {
        "todo_name": "Finalize Q3 Marketing Report",
        "priority": "High",
        "source": "🔒 Perso",
        "fire_or_clock": "🔥",  # True for "fire" (urgent)
        "deadline": (now_french - datetime.timedelta(days=2)),
        "status": "Done",
        "files": ["Q3_report_final_v2.docx", "presentation_slides.pptx"],
        "comments": ["Approved by Jane Doe.", "Awaiting final sign-off from legal."],
        "created_time": (now_french - datetime.timedelta(days=10)),
        "modified_time": (now_french - datetime.timedelta(days=2, hours=4)),
    },
    {
        "todo_name": "Develop User Authentication Feature",
        "priority": "High",
        "source": "🔒 Perso",
        "fire_or_clock": "🔥",
        "deadline": (now_french - datetime.timedelta(days=5)),
        "status": "Done",
        "files": ["auth_module.py", "user_schema.sql"],
        "comments": ["Deployed to production in v1.2.", "Passed all security checks."],
        "created_time": (now_french - datetime.timedelta(days=25)),
        "modified_time": (now_french - datetime.timedelta(days=5, hours=1)),
    },
    {
        "todo_name": "Book Flights for Paris Conference",
        "priority": "Medium",
        "source": "👩‍❤️‍👨 Famille",
        "fire_or_clock": "",  # False for "clock" (scheduled task)
        "deadline": (now_french - datetime.timedelta(days=15)),
        "status": "Todo",
        "files": ["flight_confirmation_AF123.pdf", "hotel_booking.pdf"],
        "comments": ["Got a window seat.", "Total cost was within budget."],
        "created_time": (now_french - datetime.timedelta(days=30)),
        "modified_time": (now_french - datetime.timedelta(days=15)),
    },
    {
        "todo_name": "Zizi pote",
        "priority": "Medium",
        "source": "🤱 Mama",
        "fire_or_clock": "⏰",  # False for "clock" (scheduled task)
        "deadline": (now_french - datetime.timedelta(days=15)),
        "status": "Todo",
        "files": ["flight_confirmation_AF123.pdf", "hotel_booking.pdf"],
        "comments": ["Got a window seat.", "Total cost was within budget."],
        "created_time": (now_french - datetime.timedelta(days=30)),
        "modified_time": (now_french - datetime.timedelta(days=15)),
    }
]


############# TITLE DUMMY DICT AND DATA FOR TESTING #############
pass
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

# Style for to-do name in to-do details window
airtable_todo_header_style = (
    'w-[85%] bg-white font-inter font-bold text-zinc-900 text-[31px] '
    'leading-[1.5] tracking-[-0.16px] px-2 py-[6px] rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

# Style for to-do details window done button
airtable_done_button_style = (
    'w-[15%] h-[40px] !bg-[#1555d9] text-white text-medium rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

# Style for to-do details window properties selector type
airtable_property_selector_style = (
    'w-full bg-white font-inter font-bold text-zinc-900 '
    'leading-[1.5] tracking-[-0.16px] px-2 py-0 rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

# Style for to-do details window mini properties heading
airtable_todo_properties_heading = 'font-inter text-zinc-900 text-[13px] leading-[1.5] font-medium'

# Style for to-do details window date type labels
airtable_date_label_style = (
    'w-full bg-white font-inter text-zinc-900'
    'leading-[1.5] tracking-[-0.16px] px-2 py-2 rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

# Style for to-do details window upload type property
airtable_upload_zone_style = (
    'max-w-full font-inter text-zinc-900'
    'leading-[1.5] tracking-[-0.16px] px-2 py-2 rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

# Style for to-do creation window create button
airtable_create_button_style = (
    'w-[15%] h-[40px] !bg-[#127b0d] text-white text-medium rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

# Dictionaries to map values to Tailwind CSS classes for color
STATUS_COLORS = {
    'Todo': 'bg-gray-200 text-gray-800',
    'In Progress': 'bg-blue-200 text-blue-800',
    'Done': 'bg-green-200 text-green-800',
}
PRIORITY_COLORS = {
    'Low': 'bg-yellow-200 text-yellow-800',
    'Medium': 'bg-orange-200 text-orange-800',
    'High': 'bg-red-200 text-red-800',
}

############# TITLE GLOBAL VARIABLES #############
pass
# UI ELEMENTS VARIABLES
# Main page elements
main_page = None

# To-do details window elements
todo_details_window = None
mark_done_btn = None
todo_header_input = None
status_property_h3 = None
priority_property_h3 = None
fire_property_h3 = None
source_property_h3 = None
status_dropdown_selector = None
priority_dropdown_selector = None
source_dropdown_selector = None
fire_dropdown_selector = None
deadline_property_h3 = None
created_time_property_h3 = None
modified_time_property_h3 = None
attachment_property_h3 = None
comments_property_h3 = None
created_time_label = None
upload_file_property = None
modified_time_label = None
comment_editor_property = None

# To-do creation window elements
todo_creation_window = None
create_todo_button = None
new_todo_name = None

# To-do grouped list view
todo_list_view = None
filter_bar = None

# This dictionary will store the user's selections
active_filters = {}

# We create placeholders for the dialog and its content area
details_dialog = None
details_content_area = None



############# TITLE CLI FUNCTIONS #############
pass
def group_todos_by_property(todos_list: list, grouping_property: str) -> dict:
    """Groups a list of to-do dictionaries by their 'status' key."""
    grouped = defaultdict(list)
    for todo in todos_list:
        grouped[todo[f"{grouping_property}"]].append(todo)
    return grouped


def create_grouped_list_view(todos_list: list, property_used_for_grouping: str):
    """Creates an Airtable-like grouped list view."""
    grouped_todos = group_todos_by_property(todos_list=todos_list, grouping_property=property_used_for_grouping)

    # Style for the to-do item rows
    item_row_style = 'w-full p-2 bg-white hover:bg-gray-50 cursor-pointer'

    # Loop through each status group (e.g., "Todo", "Done")
    for status, todos in grouped_todos.items():
        # Create a collapsible header for the group
        with ui.expansion(f'{status} ({len(todos)})', icon='drag_indicator').classes('w-full'):
            # This column holds all the to-dos for this group
            with ui.column().classes('w-full gap-0'):
                # Loop through each to-do in the current group
                for todo in todos:
                    # The main row for a single to-do item
                    with ui.row().classes('w-full p-3 items-center hover:bg-gray-50 cursor-pointer').on(
                            'click', lambda t=todo: open_todo_details(t)):
                        # To-do name (takes up all available space)
                        ui.label(todo['todo_name']).classes('flex-grow')

                        # --- NEW: Add the properties on the right ---

                        # Status "Pill"
                        status = todo.get('status', '')
                        ui.label(status).classes(
                            f'w-28 text-center text-sm p-1 rounded-full {STATUS_COLORS.get(status, "bg-gray-200")}')

                        # Fire Icon
                        is_urgent = todo.get('fire', False)
                        ui.label('🔥' if is_urgent else '').classes('w-12 text-center text-xl')

                        # Priority "Pill"
                        priority = todo.get('priority', '')
                        ui.label(priority).classes(
                            f'w-24 text-center text-sm p-1 rounded-full {PRIORITY_COLORS.get(priority, "bg-gray-200")}')

                        # Deadline
                        deadline = todo.get('deadline', '').strftime("%d/%m/%Y")
                        ui.label(deadline).classes('w-32 text-right')

                    ui.separator()


def add_todo_to_list():
    global new_todo_name, created_time_label, upload_file_property, modified_time_label, comment_editor_property, \
        status_dropdown_selector, priority_dropdown_selector, source_dropdown_selector, fire_dropdown_selector
    todo_to_be_added : dict = {
        "todo_name": new_todo_name.value,
        "priority": priority_dropdown_selector.value,
        "source": source_dropdown_selector.value,
        "fire_or_clock": fire_dropdown_selector.value,
        "deadline": "⚠️ TTTTTESSSSTTT A CORRIGER",
        "status": status_dropdown_selector.value,
        "files": "⚠️ TTTTTESSSSTTT A CORRIGER",
        "comments": comment_editor_property.value,
        "created_time": created_time_label.text,
        "modified_time": modified_time_label.text
    }

    todos_sample.append(todo_to_be_added)
    print(todos_sample)

############# TITLE LAYOUT FUNCTIONS #############
pass
def show_main_page():
    """
        Return the layout that will contain the to-do details window and to-do creation window.
        :return: main_page column element
    """
    global main_page
    main_page = ui.column().classes("w-full h-screen")
    with main_page:
        with ui.column().classes("w-full h-screen"):
            # 1. Build the creation dialog. It will be invisible until opened.
            create_dialog = build_create_todo_dialog()

            # 2. Build the main list view.
            with ui.row().classes('w-full justify-between items-center p-4 border-b'):
                create_filter_bar(active_filters)
                # 3. The button now opens the dialog.
                ui.button('New To-Do', icon='add', on_click=create_dialog.open).props('color=primary')

            # The rest of your list view
            with ui.column().classes("w-full"):
                create_grouped_list_view(todos_list=todos_sample, property_used_for_grouping="source")
    return main_page


# Orchestrates opening the details dialog ---
def open_todo_details(todo: dict):
    """Clears, populates, and opens the details dialog for a given to-do."""
    show_todo_details_window(todo)
    details_dialog.open()


def create_filter_dropdown(name: str, options: List[str], filters: Dict):
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


def create_filter_bar(filters: Dict):
    """Creates a horizontal bar of filter dropdowns."""
    with ui.row().classes('items-center gap-2 p-2'):
        ui.label('Filter by:').classes('text-gray-500')
        create_filter_dropdown('Status', STATUS_OPTIONS, filters)
        create_filter_dropdown('Priority', PRIORITY_OPTIONS, filters)
        create_filter_dropdown('Source', SOURCE_OPTIONS, filters)


def show_todo_list_view():
    """
        Return the layout that will contain the concatenated list view, grouped (for the moment) by source
        :return: todo_list_view column element
    """
    global todo_list_view, create_todo_button, filter_bar
    with ui.row().classes("w-full justify-between items-center"):
        filter_bar = create_filter_bar(active_filters)
        create_todo_button = show_create_todo_button()
    with ui.column().classes("w-full"):
        create_grouped_list_view(todos_list=todos_sample, property_used_for_grouping="source")


def show_todo_details_window(todo_to_show: dict):
    """Populates the details_content_area element with the UI for a specific to-do."""
    global details_content_area

    # Clear any previous content
    details_content_area.clear()

    # Build the UI inside the content area
    with details_content_area:
        # The scroll area is now inside the content area
        with ui.scroll_area().classes('w-full h-full'):
            # HEADER SECTION
            with ui.row().classes("w-full no-wrap items-center p-2"):
                # Pass the actual to-do name to the input
                ui.input(value=todo_to_show['todo_name']).classes(airtable_todo_header_style).props("borderless")
                ui.button(text="Mark as done").classes(airtable_done_button_style).props('no-caps')

            # 1st SECTION TO DEFINE FUNDAMENTALS ABOUT TO-DO : PRIORITY, STATUS, FIRE, SOURCE
            global status_property_h3, priority_property_h3, fire_property_h3, source_property_h3
            global status_dropdown_selector, priority_dropdown_selector, fire_dropdown_selector, source_dropdown_selector
            # Display this section as a row of 4 cells (grid element)
            with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
                with ui.grid(columns=4).classes("w-full p-2 !bg-[#f3f6fc]"):
                    # Cell N°1/4 : to-do status
                    with ui.column():
                        status_property_h3 = ui.label("Status").classes(airtable_todo_properties_heading)
                        status_dropdown_selector = ui.select(options=STATUS_OPTIONS,
                                                             value=todo_to_show["status"]).classes(
                            airtable_property_selector_style).props('dense borderless')
                    # Cell N°2/4 : to-do priority
                    with ui.column():
                        priority_property_h3 = ui.label("Priorité").classes(airtable_todo_properties_heading)
                        priority_dropdown_selector = ui.select(options=PRIORITY_OPTIONS,
                                                               value=todo_to_show["priority"]).classes(
                            airtable_property_selector_style).props('dense borderless')
                    # Cell N°3/4 : to-do fire
                    with ui.column():
                        fire_property_h3 = ui.label("Fire").classes(airtable_todo_properties_heading)
                        fire_dropdown_selector = ui.select(options=FIRE_OPTIONS,
                                                           value=todo_to_show["fire_or_clock"]).classes(
                            airtable_property_selector_style).props('dense borderless')
                    # Cell N°4/4 : to-do source
                    with ui.column():
                        source_property_h3 = ui.label("Source").classes(airtable_todo_properties_heading)
                        source_dropdown_selector = ui.select(
                            options=SOURCE_OPTIONS, value=todo_to_show["source"]).classes(
                            airtable_property_selector_style).props('dense borderless')

            # 2nd SECTION TO DEFINE DATE INFO ABOUT TO-DO : DEADLINE, CREATED TIME, LAST MODIFIED TIME
            global deadline_property_h3, created_time_property_h3, modified_time_property_h3, attachment_property_h3
            global created_time_label, modified_time_label, upload_file_property
            # Display this section as a row of 3 cells (grid element)
            with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
                with ui.grid(columns=3).classes("w-full p-2 !bg-[#f3f6fc]"):
                    # Cell N°1/3 : to-do deadline
                    with ui.column():
                        deadline_property_h3 = ui.label("Deadline").classes(airtable_todo_properties_heading)
                        with ui.input().props("dense borderless").classes(airtable_property_selector_style) as date:
                            with ui.menu().props('no-parent-event') as menu:
                                with ui.date().bind_value(date).props('mask="DD/MM/YYYY"'):
                                    with ui.row().classes('justify-end'):
                                        ui.button('Close', on_click=menu.close).props('flat')
                            with date.add_slot('append'):
                                ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                    # Cell N°2/3 : to-do creation date
                    with ui.column():
                        created_time_property_h3 = ui.label("Created on").classes(airtable_todo_properties_heading)
                        created_time_label = ui.label(text="12/03/2025").classes(airtable_date_label_style).props(
                            'dense borderless')
                    # Cell N°2/3 : to-do last modified time
                    with ui.column():
                        modified_time_property_h3 = ui.label("Modified on").classes(
                            airtable_todo_properties_heading)
                        modified_time_label = ui.label(text="28/05/2025").classes(airtable_date_label_style).props(
                            'dense borderless')

            # 3rd AND LAST SECTION TO ALLOW COMMENTS AND FILE ATTACHMENTS
            global comments_property_h3, comment_editor_property
            # Display this section as a row containing 2 columns
            with ui.row(wrap=False).classes("w-full p-2 !bg-[#f3f6fc]"):
                # Column N°1/2 : comments section
                with ui.column().classes('w-[75%]'):
                    comments_property_h3 = ui.label("Comments").classes(airtable_todo_properties_heading)
                    comment_editor_property = ui.editor(placeholder='Type something here').classes("w-full")
                # Column N°2/2 : file upload section
                with ui.column().classes('w-[25%]'):
                    attachment_property_h3 = ui.label("Attachments").classes(airtable_todo_properties_heading)
                    upload_file_property = ui.upload(
                        on_upload=lambda e: ui.notify(f'Uploaded {e.name}')).classes(
                        airtable_upload_zone_style).props(
                        'dense borderless')


def show_create_todo_button():
    global create_todo_button
    create_todo_button = ui.button(text="Create todo").classes(airtable_create_button_style).props(
        'no-caps')
    return create_todo_button


def build_create_todo_dialog() -> ui.dialog:
    """Builds the 'Create To-Do' dialog window with its content."""
    global new_todo_name
    with ui.dialog() as dialog, ui.card().classes("w-2/3 h-5/6"):
        with ui.column().classes('w-full h-full'):
            # HEADER SECTION
            with ui.row().classes("w-full no-wrap items-center p-2"):
                new_todo_name = ui.input(placeholder="Enter new to-do name...").classes(
                    airtable_todo_header_style).props("borderless")
                # This button will eventually save the new to-do
                ui.button("Create", on_click=lambda: (
                    ui.notify("To-do Created!"),
                    add_todo_to_list(),
                    dialog.close()  # Close the dialog after creation
                )).classes(airtable_create_button_style).props('no-caps')

            # CONTENT SECTION (you can add the rest of your form fields here)
            with ui.scroll_area().classes('w-full flex-grow p-4'):
                ui.label("Add properties for your new to-do below.")
                # 1st SECTION TO DEFINE FUNDAMENTALS ABOUT NEW TO-DO : PRIORITY, STATUS, FIRE, SOURCE
                global status_property_h3, priority_property_h3, fire_property_h3, source_property_h3
                global status_dropdown_selector, priority_dropdown_selector, fire_dropdown_selector, source_dropdown_selector
                # Display this section as a row of 4 cells (grid element)
                with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
                    with ui.grid(columns=4).classes("w-full p-2 !bg-[#f3f6fc]"):
                        # Cell N°1/4 : to-do status
                        with ui.column():
                            status_property_h3 = ui.label("Status").classes(airtable_todo_properties_heading)
                            status_dropdown_selector = ui.select(options=STATUS_OPTIONS, value="Todo").classes(
                                airtable_property_selector_style).props('dense borderless')
                        # Cell N°2/4 : to-do priority
                        with ui.column():
                            priority_property_h3 = ui.label("Priorité").classes(airtable_todo_properties_heading)
                            priority_dropdown_selector = ui.select(options=PRIORITY_OPTIONS,
                                                                   value="High").classes(
                                airtable_property_selector_style).props('dense borderless')
                        # Cell N°3/4 : to-do fire
                        with ui.column():
                            fire_property_h3 = ui.label("Fire").classes(airtable_todo_properties_heading)
                            fire_dropdown_selector = ui.select(options=FIRE_OPTIONS).classes(
                                airtable_property_selector_style).props('dense borderless')
                        # Cell N°4/4 : to-do source
                        with ui.column():
                            source_property_h3 = ui.label("Source").classes(airtable_todo_properties_heading)
                            source_dropdown_selector = ui.select(
                                options=SOURCE_OPTIONS).classes(
                                airtable_property_selector_style).props('dense borderless')

                # 2nd SECTION TO DEFINE DATE INFO ABOUT NEW TO-DO : DEADLINE, CREATED TIME, LAST MODIFIED TIME
                global deadline_property_h3, created_time_property_h3, modified_time_property_h3, attachment_property_h3
                global created_time_label, modified_time_label, upload_file_property
                # Display this section as a row of 3 cells (grid element)
                with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
                    with ui.grid(columns=3).classes("w-full p-2 !bg-[#f3f6fc]"):
                        # Cell N°1/3 : to-do deadline
                        with ui.column():
                            deadline_property_h3 = ui.label("Deadline").classes(airtable_todo_properties_heading)
                            with ui.input().props("dense borderless").classes(airtable_property_selector_style) as date:
                                with ui.menu().props('no-parent-event') as menu:
                                    with ui.date().bind_value(date):
                                        with ui.row().classes('justify-end'):
                                            ui.button('Close', on_click=menu.close).props('flat')
                                with date.add_slot('append'):
                                    ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                        # Cell N°2/3 : to-do creation date, now by default
                        with ui.column():
                            created_time_property_h3 = ui.label("Created on").classes(airtable_todo_properties_heading)
                            created_time_label = ui.label(text=f"{FORMATTED_FR_DATE}").classes(
                                airtable_date_label_style).props(
                                'dense borderless')
                        # Cell N°2/3 : to-do last modified time, now by default
                        with ui.column():
                            modified_time_property_h3 = ui.label("Modified on").classes(
                                airtable_todo_properties_heading)
                            modified_time_label = ui.label(text=f"{FORMATTED_FR_DATE}").classes(
                                airtable_date_label_style).props(
                                'dense borderless')

                # 3rd AND LAST SECTION TO ALLOW COMMENTS AND FILE ATTACHMENTS
                global comments_property_h3, comment_editor_property
                # Display this section as a row containing 2 columns
                with ui.row(wrap=False).classes("w-full p-2 !bg-[#f3f6fc]"):
                    # Column N°1/2 : comments section
                    with ui.column().classes('w-[75%]'):
                        comments_property_h3 = ui.label("Comments").classes(airtable_todo_properties_heading)
                        comment_editor_property = ui.editor(placeholder='Type something here').classes("w-full")
                    # Column N°2/2 : file upload section
                    with ui.column().classes('w-[25%]'):
                        attachment_property_h3 = ui.label("Attachments").classes(airtable_todo_properties_heading)
                        upload_file_property = ui.upload(
                            on_upload=lambda e: ui.notify(f'Uploaded {e.name}')).classes(
                            airtable_upload_zone_style).props(
                            'dense borderless')

    return dialog


############# TITLE MAIN LAYOUT LOGIC #############
pass
with show_main_page():
    # --- NEW: Create the reusable details dialog here. It starts hidden because it is not .open() ---
    with ui.dialog() as details_dialog, ui.card().classes("w-full h-full"):
        # This column is the container for the dynamic content
        details_content_area = ui.column().classes('w-full h-full')

# Testing
ui.run(language='fr')

