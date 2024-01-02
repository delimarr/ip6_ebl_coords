"""Base Editor."""
from ebl_coords.frontend.main_gui import Ui_MainWindow
from ebl_coords.graph_db.api import Api


class Editor:
    """Base Class for any Editors."""

    def __init__(self, ui: Ui_MainWindow, graph_db: Api) -> None:
        """Initialize the editor with a windows and a graph_db api.

        Args:
            ui (Ui_MainWindow): main window
            graph_db (Api): graph db api
        """
        self.ui = ui
        self.graph_db = graph_db

    def reset(self) -> None:
        """Clears all text field and resets the values to the default.

        Raises:
            NotImplementedError: Needs to be overriden.
        """
        raise NotImplementedError()

    def save(self) -> None:
        """Save and reset.

        Raises:
            NotImplementedError: Needs to be overriden.
        """
        raise NotImplementedError()
