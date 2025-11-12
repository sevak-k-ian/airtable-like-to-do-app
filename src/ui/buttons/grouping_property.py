from nicegui import ui


class GroupingPropertyButton:
    @staticmethod
    def display() -> None:
        grouping_property_button = ui.button('Group by').classes(
            "bg-blue rounded text-white font-semibold px-6 py-4 text-lg").props("no-caps")

if __name__ in {"__main__", "__mp_main__"}:
    GroupingPropertyButton().display()
    ui.run(language='fr')
