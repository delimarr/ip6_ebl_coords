"""Observer in order to detect if trainswitch is occupied."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.db_cmd import OccupyNextEdgeCommand
from ebl_coords.backend.observable.observer import Observer
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from ebl_coords.main import MainWindow


class TsHitObserver(Observer):
    """Trainswitch hit observer."""

    def __init__(self, main_window: MainWindow) -> None:
        """Initialize refrence of command queue and ui.

        Args:
            main_window (MainWindow): main window
        """
        self.command_queue = main_window.command_queue
        self.ecos_df = main_window.ecos_df
        self.map_editor = main_window.map_editor

    @override
    def update(self) -> None:
        """Update QCombobox in map editor."""
        self.command_queue.put(
            OccupyNextEdgeCommand(
                content=(self.result[0], self.ecos_df), context=self.map_editor
            )
        )
