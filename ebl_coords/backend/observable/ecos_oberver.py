"""Observer in order to receive ecos updates."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.pd_cmd import UpdateStateCommand
from ebl_coords.backend.command.sandbox_cmd import RedrawCommand
from ebl_coords.backend.observable.observer import Observer
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from ebl_coords.main import MainWindow


class EcosObserver(Observer):
    """Obersver pattern for ecos.

    Args:
        Observer (_type_): interface
    """

    def __init__(self, main_window: MainWindow) -> None:
        """Initialize with ecos dataframe and command queue.

        Args:
            main_window (MainWindow): main window
        """
        self.command_queue = main_window.command_queue
        self.ecos_df = main_window.ecos_df
        self.map_editor = main_window.map_editor

    @override
    def update(self) -> None:
        """Put update command in queue."""
        self.command_queue.put(
            UpdateStateCommand(content=self.result, context=self.ecos_df)
        )

        self.command_queue.put(RedrawCommand(context=self.map_editor))
