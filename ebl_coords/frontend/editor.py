"""Base Editor."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ebl_coords.main import MainWindow


class Editor:
    """Base Class for any Editors."""

    def __init__(self, main_window: MainWindow) -> None:
        """Initialize the Editor with a main_window.

        Args:
            main_window (MainWindow): main_window
        """
        self.main_window = main_window
        self.ui = main_window.ui
        self.graph_db = main_window.graph_db
        self.gtcommand = main_window.gtcommand

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
