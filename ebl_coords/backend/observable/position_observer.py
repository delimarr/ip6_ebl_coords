"""Observer to calculate distance, velocity."""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ebl_coords.backend.command.gui_cmd import AddFloatCommand, SetTextCommand
from ebl_coords.backend.command.gui_cmd import UpdateMapCommand
from ebl_coords.backend.constants import MIN_DELTA_DISTANCE
from ebl_coords.backend.observable.observer import Observer
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from ebl_coords.main import MainWindow


class PositionObserver(Observer):
    """React to incoming different coordinates."""

    def __init__(self, main_window: MainWindow) -> None:
        """Initialize with main window.

        Args:
            main_window (MainWindow): main window
        """
        self.command_queue = main_window.command_queue
        self.ui = main_window.ui
        self.map_editor = main_window.map_editor
        self.prev_coord: np.ndarray | None = None
        self.prev_timestamp: int | None = None  # in ms

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
            self.command_queue.put(
                AddFloatCommand(content=distance, context=self.ui.map_distance_dsb)
            )
            self.command_queue.put(
                SetTextCommand(
                    content=f"{(distance / time_delta):.3f}",
                    context=self.ui.map_v_label,
                )
            )
            self.command_queue.put(UpdateMapCommand(context=self.map_editor))

            self.prev_coord = coord
            self.prev_timestamp = timestamp
