import logging
from typing import Optional
from nicegui import ui
from src.ui.components.filter_button import FilterButton
# from src.models.database import AuthorizedPropertiesOptions

# Configure logging at module level
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class FilterBar:
    """
    A horizontal toolbar containing multiple FilterButton components.

    The FilterBar acts as a container and coordinator for filter buttons. It:
    1. Holds references to all FilterButton instances
    2. Maintains an aggregated dictionary of all current selections across all buttons
    3. Updates this dictionary whenever any button's selection changes

    This creates a parent-child relationship where:
    - FilterBar (parent) owns the buttons and aggregated state
    - FilterButton (child) handles individual filter logic
    - Communication flows: FilterButton → FilterBar via callbacks

    Attributes:
        buttons: Tuple of all FilterButton instances in this bar
        user_selection: Dictionary mapping button names to their current selections
            Example: {"Status": ["Open", "In Progress"], "Priority": ["High"]}
    """

    def __init__(self, *all_filter_buttons: FilterButton) -> None:
        """
        Initialize a FilterBar with multiple FilterButton instances.

        Args:
            *all_filter_buttons: Variable number of FilterButton instances to include
                in this bar. Using *args allows flexible numbers of buttons:
                FilterBar(btn1) or FilterBar(btn1, btn2, btn3) both work.

        Example:
            status_btn = FilterButton("Status", ["Open", "Closed"])
            priority_btn = FilterButton("Priority", ["High", "Low"])
            bar = FilterBar(status_btn, priority_btn)
        """
        # Store buttons as a tuple (immutable) since the set of buttons shouldn't change
        self.buttons = all_filter_buttons

        # Initialize user_selection with current state of all buttons
        # At initialization, all buttons have empty current_selection lists
        self.user_selection: dict[str, list[str]] = {
            filter_button.button_name: filter_button.current_selection
            for filter_button in all_filter_buttons
        }

    def display(self) -> Optional[ui.row]:
        """
        Create and display the FilterBar UI with all its buttons.

        This method performs the critical connection between FilterBar and FilterButtons:
        1. Creates a horizontal row container (ui.row)
        2. Loops through all buttons
        3. Passes self.update_user_selection to each button as a callback
        4. Each button will call this callback whenever its selection changes

        CALLBACK PATTERN: This is where the parent-child communication is established.
        Each FilterButton receives a reference to the FilterBar's update method.
        When a button's selection changes, it calls this method, which rebuilds
        the aggregated user_selection dictionary.

        Returns:
            The ui.row element containing all buttons, or None if creation fails.

        Raises:
            Exception: Any error during UI creation is logged and re-raised
        """
        try:
            # Create a horizontal row with spacing and padding for visual organization
            with ui.row().classes('items-center gap-2 p-2') as filtering_bar:
                # Display each button and establish the callback connection
                for button in self.buttons:
                    # CRITICAL: Pass our update method as the callback
                    # When this button's selection changes, it will call self.update_user_selection
                    button.display(self.update_user_selection)

            logger.info(
                f"✅ Successfully created FilterBar with {len(self.buttons)} buttons. "
                f"Callback connections established."
            )
            return filtering_bar

        except Exception as error:
            # Log the specific error type and message for debugging
            logger.error(
                f"🛑 Failed to create FilterBar UI: {type(error).__name__}: {error}",
                exc_info=True  # This includes the full stack trace in logs
            )
            # Re-raise so the caller knows something went wrong
            # Don't silently swallow errors!
            raise

    def update_user_selection(self) -> None:
        """
        Rebuild the aggregated selection dictionary from all buttons' current states.

        This method is called by FilterButton instances whenever their selection changes.
        It rebuilds the entire user_selection dictionary by querying each button's
        current_selection attribute.

        WHY REBUILD THE WHOLE DICTIONARY?
        - Simple and reliable: always guaranteed to be in sync
        - Avoids complex state management and potential inconsistencies
        - Performance is fine for typical numbers of buttons (<100)

        Raises:
            AttributeError: If a button doesn't have current_selection (shouldn't happen)
            Exception: Any other unexpected error during dictionary rebuild
        """
        try:
            # Rebuild the dictionary from scratch by querying all buttons
            self.user_selection = {
                filter_button.button_name: filter_button.current_selection
                for filter_button in self.buttons
            }

            logger.info(
                f"✅ Updated FilterBar.user_selection. Current state: {self.user_selection}"
            )

        except AttributeError as error:
            # This would happen if a button somehow lost its current_selection attribute
            logger.error(
                f"🛑 Button missing 'current_selection' attribute: {error}",
                exc_info=True
            )
            raise

        except Exception as error:
            # Catch-all for unexpected errors
            logger.error(
                f"🛑 Unexpected error updating user_selection: {type(error).__name__}: {error}",
                exc_info=True
            )
            raise


if __name__ in {"__main__", "__mp_main__"}:
    # Example usage: Create buttons and a bar
    status_button = FilterButton("Status", AuthorizedPropertiesOptions.STATUS_OPTIONS)
    priority_button = FilterButton("Priority", AuthorizedPropertiesOptions.PRIORITY_OPTIONS)
    source_button = FilterButton("Source", AuthorizedPropertiesOptions.SOURCE_OPTIONS)

    # Create the FilterBar with all buttons
    filter_bar = FilterBar(status_button, priority_button, source_button)

    # Display the UI - this establishes callback connections
    filter_bar.display()

    # Add a debug display to see the current selection state
    ui.label().bind_text_from(
        filter_bar,
        'user_selection',
        backward=lambda x: f"Current selections: {x}"
    )

    ui.run(language='fr')
