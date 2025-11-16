from nicegui import ui
from src.models.database import AuthorizedPropertiesOptions
from src.styles.constants import AT_TODO_HEADER_STYLE, AT_PROPERTY_SELECTOR_STYLE, AT_DATE_LABEL_STYLE, \
    AT_UPLOAD_ZONE_STYLE, AT_TODO_PROPERTIES_HEADING, GOOGLE_INTER_FONT
from src.styles.buttons import AT_EDIT_BTN_STYLE
from src.ui.buttons.edit_todo import EditButton
from src.ui.buttons.delete_todo import DeleteButton
from src.services.file_service import FileManager


class TodoDetailsDialog:
    def __init__(self, todo_dict: dict):
        """Initializes the object without assigning yet the value. They will be assigned during display() moment.
        Design/architecture choice: I made the choice to create a full class for "existing todo" dialogs. I’ll make an other class, for TodoCreationDialog that will repeat a
        lot of ui and design patterns from this one, but despite doing some Repeat Myself, it will be more clear and maintainable.
        """
        self.todo_dict = todo_dict
        self.todo_id = None
        self.name_input = None
        self.status_select = None
        self.priority_select = None
        self.fire_or_clock_select = None
        self.source_select = None
        self.deadline_input = None
        self.created_time_label = None
        self.modified_time_label = None
        self.comments_editor = None
        self.attachment_dir_label = None
        # Create a FileManager attribute to save all files upload operations related to that instance of TodoDetailDialog
        self.file_manager = FileManager()

    def display(self) -> int:
        # Assign first todo_id
        self.todo_id = self.todo_dict["id"]

        # Create the dialog ui + all his children components that will take instance’s attribute values from todo_dict
        with ui.dialog(value=True).props("full-width full-height") as todo_dialog:
            with ui.column().classes('w-full h-full !bg-[#f3f6fc] p-4') as main_container:
                # HEADER SECTION (to-do name + CTA)
                with ui.row().classes("w-full no-wrap items-center p-2"):
                    self.name_input = ui.input(value=self.todo_dict['todo_name']).classes(AT_TODO_HEADER_STYLE).props(
                        "borderless")

                    # Display Edit button
                    EditButton(callback_function_on_click=self.handle_todo_edit)

                    # Display Delete button
                    DeleteButton(callback_function_on_click=self.handle_todo_delete)

                # 1st SECTION (4 cells grid element in a row) : PRIORITY, STATUS, FIRE, SOURCE
                with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
                    with ui.grid(columns=4).classes("w-full p-2 !bg-[#f3f6fc]"):
                        # 1/4 : status
                        self.status_select = ui.select(options=AuthorizedPropertiesOptions.STATUS_OPTIONS,
                                                       value=self.todo_dict["status"]).classes(
                            AT_PROPERTY_SELECTOR_STYLE).props(
                            'dense borderless')
                        # 2/4 : priority
                        self.priority_select = ui.select(options=AuthorizedPropertiesOptions.PRIORITY_OPTIONS,
                                                         value=self.todo_dict["priority"]).classes(
                            AT_PROPERTY_SELECTOR_STYLE).props(
                            'dense borderless')
                        # 3/4 : fire
                        self.fire_or_clock_select = ui.select(options=AuthorizedPropertiesOptions.FIRE_OPTIONS,
                                                              value=self.todo_dict["fire_or_clock"]).classes(
                            AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')
                        # 4/4 : source
                        self.source_select = ui.select(
                            options=AuthorizedPropertiesOptions.SOURCE_OPTIONS, value=self.todo_dict["source"]).classes(
                            AT_PROPERTY_SELECTOR_STYLE).props('dense borderless')

                # 2nd SECTION (3 cells grid element in a row) : DEADLINE, CREATED TIME, LAST MODIFIED TIME
                with ui.row().classes("bg-green w-full p-2 !bg-[#f3f6fc] justify-between"):
                    with ui.grid(columns=3).classes("w-full p-2 !bg-[#f3f6fc]"):
                        # 1/3 : deadline
                        with ui.column():
                            ui.label("Deadline").classes(AT_TODO_PROPERTIES_HEADING)
                            self.deadline_input = ui.input(value=self.todo_dict["deadline"]).props(
                                "dense borderless").classes(
                                AT_PROPERTY_SELECTOR_STYLE)
                        # 2/3 : creation date
                        with ui.column():
                            ui.label("Created on").classes(AT_TODO_PROPERTIES_HEADING)
                            self.created_time_label = ui.label(text=f"{self.todo_dict["created_time"]}").classes(
                                AT_DATE_LABEL_STYLE).props(
                                'dense borderless')

                        # 3/3 : last modified time
                        with ui.column():
                            ui.label("Modified on").classes(AT_TODO_PROPERTIES_HEADING)
                            self.modified_time_label = ui.label(text=f"{self.todo_dict["modified_time"]}").classes(
                                AT_DATE_LABEL_STYLE).props(
                                'dense borderless')

                # 3rd SECTION (2 cols in a row) : COMMENTS & FILE ATTACHMENTS
                with ui.row(wrap=False).classes("w-full p-2 !bg-[#f3f6fc]"):
                    # 1/2 : comments section
                    with ui.column().classes('w-[70%]'):
                        ui.label("Comments").classes(AT_TODO_PROPERTIES_HEADING)
                        self.comments_editor = ui.editor(placeholder='Type something here').classes("w-full")
                    # 2/2 : file upload section
                    with ui.column().classes('w-[30%]'):
                        ui.label(" ").classes(AT_TODO_PROPERTIES_HEADING)
                        ui.label(" ").classes(AT_TODO_PROPERTIES_HEADING)
                        with ui.row().classes("w-full justify-between items-center"):
                            # Get folder’s name as saved in the database
                            todo_folder_name_saved_in_database = self.todo_dict["attachment_dir"]
                            # Display folder’s name in UI
                            folder_name_label = ui.label(text=f"📁 {todo_folder_name_saved_in_database}")
                            # Getting values, and implement logic, to display it nicely in the UI
                            files_count: int = self.file_manager.get_folder_files_count(todo_folder_name_saved_in_database)
                            folder_files_name_list: list = self.file_manager.visualize_folder_files_names(todo_folder_name_saved_in_database)
                            folder_files_names: str = "    ".join([f"📄 {file}" for file in folder_files_name_list])
                            if files_count > 0:
                                ui.label(text=f"{files_count} files saved: \n{folder_files_names}").style(
                                    'white-space: pre-wrap;')
                            elif files_count == 0:
                                ui.label(text="No files saved yet.")

                            self.attachment_dir_label = ui.upload(multiple=True, on_upload=lambda e:self.file_manager.temporary_save_uploaded_files(e)).classes(AT_UPLOAD_ZONE_STYLE).props(
                                'dense borderless')
        return self.todo_id

    async def handle_todo_edit(self):
        database_access = TodoDatabase("../../../todos.db")

        current_name = self.name_input.value
        current_status = self.status_select.value
        current_priority = self.priority_select.value
        current_fire = self.fire_or_clock_select.value
        current_source = self.source_select.value
        current_deadline = self.deadline_input.value
        current_modified = self.modified_time_label.text
        current_created = self.created_time_label.text
        current_comments = self.comments_editor.value

        database_access.update_entire_todo(todo_id=self.todo_id, todo_name=current_name, status=current_status,
                              priority=current_priority, fire_or_clock=current_fire, source=current_source,
                              deadline=current_deadline, comments=current_comments)

        ui.notify("Edited successfully")

        # Save locally the files that have been temporarily uploaded
        await self.file_manager.flush_uploads(self.todo_dict["attachment_dir"])

    def handle_todo_delete(self):
        # Get access to todos database
        database_access = TodoDatabase("../../../todos.db")

        # Get the todo_id that will be deleted
        self.todo_id = self.todo_dict["id"]

        # Get the attachment_dir string saved for this todo in the database
        local_todo_folder_name = str(self.todo_dict["attachment_dir"])

        # Delete the local folder related to that todo
        FileManager().delete_folder(local_todo_folder_name)

        # Delete the todo inside the database
        database_access.delete_todo(self.todo_id)

        # Notify user of the succuss of the deletion process
        ui.notify("Deleted successfully")



    ############ TESTING ############


if __name__ in {"__main__", "__mp_main__"}:
    # Connect to Database
    from src.models.database import TodoDatabase

    db = TodoDatabase("../../../todos.db")

    # Retrieve todo data from database
    todo_from_database = db.get_todo_by_id(4)
    todo_data = dict(todo_from_database)

    displayed_todo = TodoDetailsDialog(todo_data)
    displayed_todo.display()

    # ----APP RUNNING----
    ui.run(language='fr')
