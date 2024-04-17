"""Observer in order to detect if trainswitch is occupied."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import Command
from ebl_coords.backend.command.db_cmd import OccupyNextEdgeGuiCommand
from ebl_coords.backend.observable.gtcommand_subject import GtCommandSubject
from ebl_coords.backend.observable.observer import Observer
from ebl_coords.decorators import override
from ebl_coords.frontend.command.d_spinbox_cmd import SetFloatCmd

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QComboBox

    from ebl_coords.main import EblCoords


class TsHitObserver(Observer):
    """Trainswitch hit observer."""

    def __init__(
        self,
        ebl_coors: EblCoords,
        combo_box: QComboBox,
    ) -> None:
        """Initialize TsHitObserver.

        Args:
            ebl_coors (EblCoords): ebl_Coords
            combo_box (QComboBox): map combo box
        """
        self.ebl_coords = ebl_coors
        self.gui_queue = ebl_coors.gui_queue
        self.worker_queue = ebl_coors.worker_queue
        self.combo_box = combo_box

    @override
    def update(self) -> None:
        """Update QCombobox in map editor."""
        self.worker_queue.put(
            OccupyNextEdgeGuiCommand(
                content=(self.result[0], self.ebl_coords, self.combo_box),
                context=self.gui_queue,
            )
        )
        self.gui_queue.put(SetFloatCmd(content=0, context=self.ebl_coords.gui.ui.map_distance_dsb))


class AttachTsHitObsCommand(Command):
    """Create and attach a TsHitObserver."""

    def __init__(self, content: tuple[EblCoords, QComboBox]) -> None:
        """Initialize this command and set context to GtCommandSubject.

        Args:
            content (tuple[EblCoords, QComboBox]): (ebl_coords, combo_box)
        """
        super().__init__(content, GtCommandSubject())
        self.content: tuple[EblCoords, QComboBox]
        self.context: GtCommandSubject

    @override
    def run(self) -> None:
        """Create and attach a new TsHitObserver."""
        ebl_coords, combo_box = self.content
        self.context.attach_ts_hit(
            TsHitObserver(
                ebl_coors=ebl_coords,
                combo_box=combo_box,
            )
        )
