import logging

from nicegui import ui
from src.ui.components.filter_button import FilterButton
from src.models.database import AuthorizedPropertiesOptions


class FilterBar:
    def __init__(self, *all_filter_buttons: tuple[FilterButton]) -> "FilterBar":
        """
        Initializes a FilterBar object that is a collection of FilterButton objects.

        Attributes:
            *all_filter_buttons: accept an undefined number of FilterButton instances reunited inside a tuple.

        Returns:
            FilterBar instance.
        """
        self.buttons = all_filter_buttons
        self.user_selection: dict = {filter_button.button_name: filter_button.current_selection for filter_button in
                                     all_filter_buttons}

    def display(self) -> ui.row:
        """
        Creates a NiceGUI ui.row element that is composed of all the FilterButton instances used as argument.

        It loops through the tuple argument to display horizontally aligned all the FilterButtons.

        It uses a FilterBar method as argument of the FilterButton.display method in order to update FilterBar attribute
        self.user_selection everytime a change is made on FilterButton.

        Returns:
            ui.row element
        """
        try:
            with ui.row().classes('items-center gap-2 p-2') as nav_bar:
                for button in self.buttons:
                    button.display(self.update_user_selection)
            logging.info("✅Successfully created the FilterBar element and passed FilterBar.update_user_selection method to each FilterButton.")
        except:
            logging.error("🛑 Did not create the FilterBar element")

    def update_user_selection(self):
        """
        Method that updates the FilterBar attribute self.user_selection data.
        This method will be used as an argument of the FilterButton.display method in order to trigger this FilterBar function
        everytime a FilterButton is changed.
        :return:
        """
        try:
            self.user_selection: dict = {filter_button.button_name: filter_button.current_selection for filter_button in
                                        self.buttons}
            logging.info(
                "✅Successfully updated FilterBar dict attribute user_selection.")
        except:
            logging.error("🛑 Did not updated FilterBar dict attribute user_selection.")

if __name__ in {"__main__", "__mp_main__"}:
    status_button = FilterButton("Status", AuthorizedPropertiesOptions.STATUS_OPTIONS)
    priority_button = FilterButton("Priority", AuthorizedPropertiesOptions.PRIORITY_OPTIONS)
    source_button = FilterButton("Source", AuthorizedPropertiesOptions.SOURCE_OPTIONS)

    filter_bar = FilterBar(status_button, priority_button, source_button)
    filter_bar.display()

    ui.run(language='fr')
