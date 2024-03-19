"""Observer in order to detect if trainswitch is occupied."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import Command
from ebl_coords.backend.command.db_cmd import OccupyNextEdgeGuiCommand
from ebl_coords.backend.observable.gtcommand_subject import GtCommandSubject
from ebl_coords.backend.observable.observer import Observer
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from queue import Queue

    import pandas as pd
    from PyQt6.QtWidgets import QComboBox


class TsHitObserver(Observer):
    """Trainswitch hit observer."""

    def __init__(
        self,
        gui_queue: Queue[Command],
        worker_queue: Queue[Command],
        ecos_df: pd.DataFrame,
        combo_box: QComboBox,
    ) -> None:
        """Initialize TsHitObserver.

        Args:
            gui_queue (Queue[Command]): gui_queue
            worker_queue (Queue[Command]): worker_queue
            ecos_df (pd.DataFrame): ecos_df
            combo_box (QComboBox): map combo box
        """
        self.gui_queue = gui_queue
        self.worker_queue = worker_queue
        self.ecos_df = ecos_df
        self.combo_box = combo_box

    @override
    def update(self) -> None:
        """Update QCombobox in map editor."""
        self.worker_queue.put(
            OccupyNextEdgeGuiCommand(
                content=(self.result[0], self.ecos_df, self.combo_box),
                context=self.gui_queue,
            )
        )


class AttachTsHitObsCommand(Command):
    """Create and attach a TsHitObserver."""

    def __init__(
        self, content: tuple[Queue[Command], Queue[Command], pd.DataFrame, QComboBox]
    ) -> None:
        """Initialize this command and set context to GtCommandSubject.

        Args:
            content (tuple[Queue[Command], Queue[Command], pd.DataFrame, QComboBox]): (gui_queue, worker_queue, ecos_df, combo_boc)
        """
        super().__init__(content, GtCommandSubject())
        self.content: tuple[Queue[Command], Queue[Command], pd.DataFrame, QComboBox]
        self.context: GtCommandSubject

    @override
    def run(self) -> None:
        """Create and attach a new TsHitObserver."""
        gui_queue, worker_queue, ecos_df, combo_box = self.content
        self.context.attach_ts_hit(
            TsHitObserver(
                gui_queue=gui_queue,
                worker_queue=worker_queue,
                ecos_df=ecos_df,
                combo_box=combo_box,
            )
        )
