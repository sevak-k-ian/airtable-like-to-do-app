from nicegui import ui
from src.models.database import AuthorizedPropertiesOptions
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class FilterButton:
    def __init__(self, button_name: str, available_choices: list[str]) -> "FilterButton":
        """
            Initializes a Filter button that represents a todo property that can be used as a filter by the user.

            A FilterButton instance is composed of a name (attribute), a series of possibles choices/values (attribute) and
            a list (not an attribute) created at instance initialization moment that will keep tracks of the selected values
            given by NiceGUI .value attribute.

            Args:
                button_name (str) : name of the todo property used as a filter tool
                available_choices (list[str]): list coming from Database.py file class

            Returns:
                FilterButton element that will be used as an arg inside of a filter bar object.

            Raises:
                Nothing.
        """
        self.button_name = button_name
        self.available_choices = available_choices
        self.current_selection = []


    @classmethod
    def button_design(cls) -> ui.button:
        """
        Creates a NiceGUI ui.button element with Airtable-like design inspiration.

        Returns:
            ui.button element
        """
        # The button that will anchor the menu
        airtable_shadow = 'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
        dimensions = 'mr-2 px-[6px] py-[1px]'

        button = ui.button().props('flat no-caps').classes(
            f'bg-white hover:bg-gray-100 rounded-md inline-flex {airtable_shadow} {dimensions}')

        return button

    def options_selector(self, filter_bar_selection_update_method) -> ui.select:
        """
        Method that creates a NiceGUI ui.select element that use the instance’s arguments.
        On_change (when a selection is made on that gui element) it triggers an private internal function called update_filter_selection_data().

        Args:
            on_change_selector_callback_function: function that is triggered everytime a change is made on the ui.select element.
             It will use a FilterBar’s method as a callback, which is self.update_user_selection which updates a dict
             that is an attribute of a FilterBar instance, that records all choices made on all FilterButtons of the FilterBar.

        Returns:
            NiceGUI ui.select element

        Raises:
        """
        selector = ui.select(options=self.available_choices, multiple=True, label=self.button_name,
                             on_change=lambda: update_filter_selection_data()).classes(
            'min-w-44 flex').props(
            'use-chips borderless')

        def update_filter_selection_data():
            """
            Private internal function to options_selector method that is triggered everytime a change is made on the ui.select element.
            This private function will :
                - update the FilterButton instance attribute "self.current_selection" by reattributing the ui.select’s value to this attribute
                - trigger a method of the FilterBar’s object that keeps tracks of all FilterButtons’ current selections.
            """
            try:
                # Reassign current ui.select element value to self.current_selection attribute.
                self.current_selection = selector.value
                logger.info(f"✅ Successfully updated choice made on button ’{self.button_name}’.")
                # Triggers the FilterBar methods that updates its own dict of FilterButtons choices.
                filter_bar_selection_update_method()
                logger.info(f"✅ Successfully updated filter bar’s data.")
            except:
                logger.error(
                    f"🛑 Did not updated choice made on button ’{self.button_name}, neither updated filter bar’s data.")


    def display(self, filter_bar_selection_update_method) -> ui.button:
        """
        Generates a NiceGUI button thanks to class method "button_design" and fills up that button with an ui.select element
        thanks to object’s method "options_selector".

        Args:
            filter_bar_selection_update_method: allows the FilterBar object to be initialized with all Buttons choices when there are first displayed.
        """
        button = self.__class__.button_design()
        with button:
            self.options_selector(filter_bar_selection_update_method)


if __name__ in {"__main__", "__mp_main__"}:
    FilterButton("Status", AuthorizedPropertiesOptions.STATUS_OPTIONS).display()
    ui.run(language='fr')