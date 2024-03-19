"""Base Editor."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ebl_coords.frontend.gui import Gui


class Editor:
    """Base Class for any Editors."""

    def __init__(self, gui: Gui) -> None:
        """Initialize the Editor from a gui.

        Args:
            gui (Gui): the main gui
        """
        self.gui = gui
        self.ui = gui.ui
        self.worker_queue = gui.worker_queue
        self.gui_queue = gui.gui_queue

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
