"""Observer to calculate distance, velocity."""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ebl_coords.backend.command.command import Command
from ebl_coords.backend.constants import MIN_DELTA_DISTANCE, MIN_SHOW_DISTANCE
from ebl_coords.backend.observable.gtcommand_subject import GtCommandSubject
from ebl_coords.backend.observable.observer import Observer
from ebl_coords.decorators import override
from ebl_coords.frontend.command.d_spinbox_cmd import AddFloatCmd
from ebl_coords.frontend.command.label_cmd import SetTextCmd

if TYPE_CHECKING:
    from ebl_coords.frontend.map_editor import MapEditor


class PositionObserver(Observer):
    """React to incoming different coordinates."""

    def __init__(self, map_editor: MapEditor) -> None:
        """Initialize this oberver with a map_editor.

        Args:
            map_editor (MapEditor): map_editor
        """
        self.gui_queue = map_editor.gui_queue
        self.map_editor = map_editor
        self.prev_coord: np.ndarray | None = None
        self.prev_timestamp: int | None = None  # in ms
        self.distance: float = 0
        self.time_delta: float = 0

    @override
    def update(self) -> None:
        """Save the last used coordinate, until distance > MIN_TS_THRESHOLD was measured.

        Update the GUI.
        """
        assert self.result is not None
        if self.prev_coord is None:
            assert self.prev_timestamp is None
            self.prev_timestamp, self.prev_coord = self.result
            return
        timestamp, coord = self.result
        distance = np.linalg.norm(coord - self.prev_coord) / 1000
        time_delta = (timestamp - self.prev_timestamp) / 1000

        if distance > MIN_DELTA_DISTANCE:
            self.distance += distance
            self.time_delta += time_delta
            if self.distance > MIN_SHOW_DISTANCE:
                self.gui_queue.put(
                    AddFloatCmd(content=self.distance, context=self.map_editor.ui.map_distance_dsb)
                )
                v = self.distance / self.time_delta
                self.gui_queue.put(
                    SetTextCmd(
                        content=f"{v:.3f}",
                        context=self.map_editor.ui.map_v_label,
                    )
                )
                a = self.map_editor.ui.map_break_a_txt.value()
                self.gui_queue.put(
                    SetTextCmd(
                        content=f"{abs(v*v/2*a):.3f}",
                        context=self.map_editor.ui.map_break_s_label,
                    )
                )
                self.distance = 0
                self.time_delta = 0
                self.distance = 0
                self.time_delta = 0

            self.prev_coord = coord
            self.prev_timestamp = timestamp


class AttachPositionCommand(Command):
    """Create and Attach TsMeasureObserver-Command."""

    def __init__(self, content: MapEditor) -> None:
        """Create and attach a PositionObserver and set context to GtCommandSubject.

        Args:
            content (MapEditor): map_editor
        """
        super().__init__(content, GtCommandSubject())
        self.context: GtCommandSubject
        self.content: MapEditor

    @override
    def run(self) -> None:
        """Create and attach a PositionObserver."""
        self.context.attach_changed_coord(PositionObserver(map_editor=self.content))
