##############################################
# DUMMY DICT AND DATA FOR TESTING
##############################################
import datetime

# Get current time to generate realistic timestamps
now = datetime.datetime.now(datetime.timezone.utc)

todos_sample = [
    {
        "todo_name": "Finalize Q3 Marketing Report",
        "priority": "High",
        "source": "Email from Management",
        "fire_or_clock": True,  # True for "fire" (urgent)
        "deadline": (now - datetime.timedelta(days=2)).isoformat(),
        "status": "Completed",
        "files": ["Q3_report_final_v2.docx", "presentation_slides.pptx"],
        "comments": ["Approved by Jane Doe.", "Awaiting final sign-off from legal."],
        "created_time": (now - datetime.timedelta(days=10)).isoformat(),
        "modified_time": (now - datetime.timedelta(days=2, hours=4)).isoformat(),
    },
    {
        "todo_name": "Develop User Authentication Feature",
        "priority": "High",
        "source": "Project Sprint Plan",
        "fire_or_clock": True,
        "deadline": (now - datetime.timedelta(days=5)).isoformat(),
        "status": "Completed",
        "files": ["auth_module.py", "user_schema.sql"],
        "comments": ["Deployed to production in v1.2.", "Passed all security checks."],
        "created_time": (now - datetime.timedelta(days=25)).isoformat(),
        "modified_time": (now - datetime.timedelta(days=5, hours=1)).isoformat(),
    },
    {
        "todo_name": "Book Flights for Paris Conference",
        "priority": "Medium",
        "source": "Personal Reminder",
        "fire_or_clock": False,  # False for "clock" (scheduled task)
        "deadline": (now - datetime.timedelta(days=15)).isoformat(),
        "status": "Completed",
        "files": ["flight_confirmation_AF123.pdf", "hotel_booking.pdf"],
        "comments": ["Got a window seat.", "Total cost was within budget."],
        "created_time": (now - datetime.timedelta(days=30)).isoformat(),
        "modified_time": (now - datetime.timedelta(days=15)).isoformat(),
    }
]
##############################################
# LIBRARIES AND MODULES
##############################################
from nicegui import app, ui

##############################################
# AIRTABLE-LIKE STYLE DEFINITIONS
##############################################
# Load the "Inter" font from Google Fonts for the whole page.
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
##############################################
# GLOBAL VARIABLES
##############################################
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




##############################################
# LAYOUT FUNCTIONS
##############################################
def show_main_page():
    """
        Return the layout that will contain the to-do details window and to-do creation window.
        :return: main_page column element
    """
    global main_page
    main_page = ui.column().classes("w-full h-screen justify-center items-center")
    return main_page


def show_todo_details_window(todo_to_show: dict):
    """
        Return the card element that reprensents and stores all information about an existing to-do.
        :param todo_to_show:
        :return: to-do details window card element
    """
    global todo_details_window, todo_header_input, mark_done_btn
    # Define to-do details window as a big card element
    todo_details_window = ui.card().classes("w-full h-full")

    # DESIGN OF THAT TO-DO DETAILS CARD ELEMENT
    with todo_details_window:
        with ui.column().classes('w-full h-full'):
            # Enable scrolling inside that card if children elements take more space than original screen height
            with ui.scroll_area().classes('flex-grow'):
                # HEADER SECTION OF TO-DO DETAILS CONTAINING TO-DO NAME AND "MARK DONE" BUTTON
                with ui.row().classes("w-full no-wrap items-center"):
                    # To-do name header element
                    todo_header_input = ui.input(value=f'{todo_to_show}').classes(airtable_todo_header_style).props(
                        "borderless")
                    # Mark done button element
                    mark_done_btn = ui.button(text="Mark as done").classes(airtable_done_button_style).props('no-caps')

                # 1st SECTION TO DEFINE FUNDAMENTALS ABOUT TO-DO : PRIORITY, STATUS, FIRE, SOURCE
                global status_property_h3, priority_property_h3, fire_property_h3, source_property_h3
                global status_dropdown_selector, priority_dropdown_selector, fire_dropdown_selector, source_dropdown_selector
                # Display this section as a row of 4 cells (grid element)
                with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
                    with ui.grid(columns=4).classes("w-full p-2 !bg-[#f3f6fc]"):
                        # Cell N°1/4 : to-do status
                        with ui.column():
                            status_property_h3 = ui.label("Status").classes(airtable_todo_properties_heading)
                            status_dropdown_selector = ui.select(options=["Todo", "Done"], value="Todo").classes(
                                airtable_property_selector_style).props('dense borderless')
                        # Cell N°2/4 : to-do priority
                        with ui.column():
                            priority_property_h3 = ui.label("Priorité").classes(airtable_todo_properties_heading)
                            priority_dropdown_selector = ui.select(options=["High", "Medium", "Low"],
                                                                   value="High").classes(
                                airtable_property_selector_style).props('dense borderless')
                        # Cell N°3/4 : to-do fire
                        with ui.column():
                            fire_property_h3 = ui.label("Fire").classes(airtable_todo_properties_heading)
                            fire_dropdown_selector = ui.select(options=["🔥", "⏰"]).classes(
                                airtable_property_selector_style).props('dense borderless')
                        # Cell N°4/4 : to-do source
                        with ui.column():
                            source_property_h3 = ui.label("Source").classes(airtable_todo_properties_heading)
                            source_dropdown_selector = ui.select(options=["Perso", "Famille", "Yeraz", "Mama"]).classes(
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
                                    with ui.date().bind_value(date):
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

def create_todo_window() :
    """
        Return the card element that reprensents the window to create a new to-do.
        :param
        :return: to-do creation window card element
    """
    global todo_creation_window, todo_header_input, create_todo_button
    # Define to-do details window as a big card element
    todo_creation_window = ui.card().classes("w-4/5 h-full")

    # DESIGN OF THAT TO-DO DETAILS CARD ELEMENT
    with todo_creation_window:
        with ui.column().classes('w-full h-full'):
            # Enable scrolling inside that card if children elements take more space than original screen height
            with ui.scroll_area().classes('flex-grow'):
                # HEADER SECTION OF TO-DO DETAILS CONTAINING TO-DO NAME AND "MARK DONE" BUTTON
                with ui.row().classes("w-full no-wrap items-center"):
                    # To-do name header element
                    todo_header_input = ui.input(placeholder="New_todo").classes(airtable_todo_header_style).props(
                        "borderless")
                    # Create to-do button element
                    create_todo_button = ui.button(text="Create todo").classes(airtable_create_button_style).props('no-caps')

                # 1st SECTION TO DEFINE FUNDAMENTALS ABOUT TO-DO : PRIORITY, STATUS, FIRE, SOURCE
                global status_property_h3, priority_property_h3, fire_property_h3, source_property_h3
                global status_dropdown_selector, priority_dropdown_selector, fire_dropdown_selector, source_dropdown_selector
                # Display this section as a row of 4 cells (grid element)
                with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
                    with ui.grid(columns=4).classes("w-full p-2 !bg-[#f3f6fc]"):
                        # Cell N°1/4 : to-do status
                        with ui.column():
                            status_property_h3 = ui.label("Status").classes(airtable_todo_properties_heading)
                            status_dropdown_selector = ui.select(options=["Todo", "Done"], value="Todo").classes(
                                airtable_property_selector_style).props('dense borderless')
                        # Cell N°2/4 : to-do priority
                        with ui.column():
                            priority_property_h3 = ui.label("Priorité").classes(airtable_todo_properties_heading)
                            priority_dropdown_selector = ui.select(options=["High", "Medium", "Low"],
                                                                   value="High").classes(
                                airtable_property_selector_style).props('dense borderless')
                        # Cell N°3/4 : to-do fire
                        with ui.column():
                            fire_property_h3 = ui.label("Fire").classes(airtable_todo_properties_heading)
                            fire_dropdown_selector = ui.select(options=["🔥", "⏰"]).classes(
                                airtable_property_selector_style).props('dense borderless')
                        # Cell N°4/4 : to-do source
                        with ui.column():
                            source_property_h3 = ui.label("Source").classes(airtable_todo_properties_heading)
                            source_dropdown_selector = ui.select(options=["Perso", "Famille", "Yeraz", "Mama"]).classes(
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
                                    with ui.date().bind_value(date):
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

##############################################
# LAYOUT LOGIC
##############################################
with show_main_page():
    show_todo_details_window(todos_sample[1]["todo_name"])
# Create to-do details layout


# View and filter all todos layout

# Testing
ui.run()
