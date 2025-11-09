from nicegui import ui
from src.models.database import AuthorizedPropertiesOptions
from typing import Callable
import logging

# Configure logging at module level
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class FilterButton:
    """
    A filter button component that allows users to select multiple values from predefined options.

    This component combines a NiceGUI button (ui.button) with a dropdown selector (ui.select) to create
    an Airtable-inspired filtering interface. Each button tracks its current selection and
    can notify a parent component (FilterBar) when selections change.

    Attributes:
        button_name: The display name of the filter (e.g., "Status", "Priority")
        available_choices: List of all possible values the user can select from
        current_selection: List of currently selected values (updated when user makes changes)
    """

    def __init__(self, button_name: str, available_choices: list[str]) -> None:
        """
        Initialize a FilterButton with a name and available choices.

        Args:
            button_name: Name of the filter property (e.g., "Status", "Priority")
            available_choices: List of valid options for this filter

        Example:
            button = FilterButton("Status", ["Open", "In Progress", "Closed"])
        """
        self.button_name = button_name
        self.available_choices = available_choices
        # Starts empty; will be populated when user makes selections
        self.current_selection = []

    @classmethod
    def button_design(cls) -> ui.button:
        """
        Create a styled button with Airtable-inspired design.

        This is a class method because the button styling is the same for all FilterButton
        instances - it doesn't depend on any instance-specific data.

        Design choices:
            - Flat design (no raised appearance)
            - White background with subtle shadow for depth
            - Hover effect for interactivity feedback
            - Compact padding to fit multiple buttons in a row

        Returns:
            A styled but empty ui.button element ready to have content added
        """
        # Airtable uses very subtle shadows for depth without being distracting
        airtable_shadow = 'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
        # Compact dimensions to fit multiple filters in the toolbar
        dimensions = 'mr-2 px-[6px] py-[1px]'

        button = ui.button().props('flat no-caps').classes(
            f'bg-white hover:bg-gray-100 rounded-md flex items-center {airtable_shadow} {dimensions}')

        return button

    def options_selector(self, on_selection_change_callback: Callable[[], None]) -> None:
        """
        Create the dropdown ui.select selector UI element inside the button.

        This method creates a multi-select dropdown that:
        1. Shows all available choices for this filter
        2. Updates the FilterButton's current_selection when changed
        3. Notifies the parent FilterBar via callback to update its aggregated selection data

        CRITICAL: This uses a closure pattern. The inner function `update_filter_selection_data`
        has access to both `selector` (from this method's scope) and `self` (from the class).
        This is why we define the function AFTER creating the selector - so `selector` exists
        in the closure's scope.

        Args:
            on_selection_change_callback: Function to call when selection changes.
                Typically this is FilterBar.update_user_selection, which aggregates
                all button selections into a single dictionary.

        Raises:
            TypeError: If the callback is not callable
            AttributeError: If selector.value cannot be accessed (shouldn't happen in normal use)
        """
        # Create the multi-select dropdown UI element
        selector = (ui.select(
            options=self.available_choices,
            multiple=True,  # Allow selecting multiple values
            label=self.button_name,
            on_change=lambda: update_filter_selection_data()  # Trigger update on any change
        ).classes('min-w-44 flex items-center').props('use-chips borderless'))

        # CLOSURE PATTERN: This inner function "closes over" both `selector` and `self`
        def update_filter_selection_data() -> None:
            """
            Update this button's selection and notify the parent FilterBar.

            This function is called every time the user changes their selection in the dropdown.
            It performs two critical tasks:
            1. Sync the button's current_selection attribute with the UI element's value
            2. Trigger the parent FilterBar to rebuild its aggregated selection dictionary

            Why use an inner function?
            - It has access to `selector` (from the outer scope) without storing it as an attribute
            - It keeps the update logic co-located with the selector creation
            - It creates a clean separation between UI state (selector.value) and data state (self.current_selection)
            """
            try:
                # Sync our data model with the UI state
                # selector.value is a list of selected options (e.g., ["Open", "In Progress"])
                self.current_selection = selector.value
                logger.info(f"✅ FilterButton '{self.button_name}' selection updated to: {self.current_selection}")

                # Notify parent FilterBar to rebuild its aggregated dictionary
                # This ensures FilterBar.user_selection always reflects current state
                on_selection_change_callback()  # Notifies the parent FilterBar via callback to update its aggregated selection data
                logger.info(f"✅ Notified FilterBar of selection change in '{self.button_name}'")


            except AttributeError as error:
                # This might happen if selector is somehow destroyed or not properly initialized
                logger.error(f"🛑 Cannot access selector.value for '{self.button_name}': {error}")

            except TypeError as error:
                # This happens if the callback isn't actually callable
                logger.error(f"🛑 Callback is not callable for '{self.button_name}': {error}")

            except Exception as error:
                # Catch-all for unexpected errors, but log them specifically
                logger.error(f"🛑 Unexpected error updating '{self.button_name}': {type(error).__name__}: {error}")

    def display(self, on_selection_change_callback: Callable[[], None]) -> None:
        """
        Create and display the complete FilterButton UI (button + dropdown).

        This method orchestrates the creation of the full filter button:
        1. Creates the styled button container (via button_design)
        2. Adds the selector dropdown inside the button (via options_selector)
        3. Establishes the callback connection to the parent FilterBar

        DESIGN NOTE: The callback is passed here (not in __init__) to avoid circular
        dependencies. When this button is created, the FilterBar might not exist yet.
        By passing the callback during display, we ensure both objects are fully
        initialized before establishing their relationship.

        Args:
            on_selection_change_callback: Function to call when selection changes.
                This is typically FilterBar.update_user_selection.

        Example usage:
            # In FilterBar.display():
            for button in self.buttons:
                button.display(self.update_user_selection)  # Pass the FilterBar's method
        """
        # Create the button container with styling
        button = self.__class__.button_design()

        # NiceGUI context manager: everything created inside this block
        # will be rendered as a child of the button
        with button:
            # Add the selector dropdown inside the button and connect the callback
            self.options_selector(on_selection_change_callback)


if __name__ in {"__main__", "__mp_main__"}:
    # Test the FilterButton independently
    # Note: Without a FilterBar, we pass a simple print function as callback
    test_button = FilterButton("Status", AuthorizedPropertiesOptions.STATUS_OPTIONS)
    test_button.display(lambda: print(f"Selection changed: {test_button.current_selection}"))
    ui.run(language='fr')
