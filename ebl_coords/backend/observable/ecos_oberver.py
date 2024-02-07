"""Observer in order to receive ecos updates."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.pd_cmd import UpdateStateCommand
from ebl_coords.backend.observable.observer import Observer
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from queue import Queue

    import pandas as pd

    from ebl_coords.backend.command.base import Command


class EcosObserver(Observer):
    """Obersver pattern for ecos.

    Args:
        Observer (_type_): interface
    """

    def __init__(self, command_queue: Queue[Command], ecos_df: pd.DataFrame) -> None:
        """Initialize with ecos dataframe and command queue.

        Args:
            command_queue (Queue[Command]): command queue
            ecos_df (pd.DataFrame): ecos dataframe
        """
        self.command_queue = command_queue
        self.ecos_df = ecos_df

    @override
    def update(self) -> None:
        """Put update command in queue."""
        self.command_queue.put(
            UpdateStateCommand(content=self.result, context=self.ecos_df)
        )
