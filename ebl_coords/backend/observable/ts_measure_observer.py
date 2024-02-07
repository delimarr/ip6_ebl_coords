"""Observer in order to measure trainswitches."""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ebl_coords.backend.command.db_cmd import DbCommand
from ebl_coords.backend.command.gui_cmd import SetTextCommand, StatusBarCommand
from ebl_coords.backend.observable.observer import Observer
from ebl_coords.decorators import override
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem

if TYPE_CHECKING:
    from queue import Queue

    from ebl_coords.backend.command.base import Command
    from ebl_coords.backend.observable.gtcommand_subject import GtCommandSubject
    from ebl_coords.frontend.main_gui import Ui_MainWindow


class TsMeasureObserver(Observer):
    """Measure trainswitch observer.

    Args:
        Observer (_type_): observer interface
    """

    def __init__(
        self,
        selected_ts: str,
        command_queue: Queue[Command],
        ui: Ui_MainWindow,
        points_needed: int = 150,
    ) -> None:
        """Initialize the observer.

        Args:
            selected_ts (str): guid of trainswitch in db.
            command_queue (Queue[Command]): put command in queue with db and Gui updates.
            ui (Ui_MainWindow): ui
            points_needed (int, optional): How many point should be used for the measurement. Defaults to 150.
        """
        self.subject: GtCommandSubject
        self.selected_ts = selected_ts
        self.command_queue = command_queue
        self.ui = ui
        self.points_needed = points_needed
        self.buffer = np.empty((points_needed, 3), dtype=np.float32)
        self.index: int = 0

    @override
    def update(self) -> None:
        """Build buffer of coords and put command into queue."""
        if self.index == self.points_needed:
            self.subject.detach(self)
            ts_coord = np.median(self.buffer, axis=0)
            double_vertex = EdgeRelation.DOUBLE_VERTEX.name
            weiche = SwitchItem.WEICHE.name
            x, y, z = ts_coord
            cmd = f"""
            MATCH(n1:{weiche}{{node_id:'{self.selected_ts}'}})-[:{double_vertex}]->(n2:{weiche})\
            SET n1.x = '{x}'\
            SET n2.x = '{x}'\
            SET n1.y = '{y}'\
            SET n2.y = '{y}'\
            SET n1.z = '{z}'\
            SET n2.z = '{z}';
            """
            self.command_queue.put(DbCommand(content=cmd))
            self.command_queue.put(
                StatusBarCommand(
                    content=f"Weiche bei: ({x}, {y}, {z}) eingemessen.", context=self.ui
                )
            )
            self.command_queue.put(
                SetTextCommand(
                    content=f"({x}, {y}, {z})", context=self.ui.weichen_coord_label
                )
            )
            return
        self.command_queue.put(
            StatusBarCommand(
                content=f"Bitte warten. Weiche wird eingemessen: {self.index}/{self.points_needed}",
                context=self.ui,
            )
        )
        self.buffer[self.index, :] = self.result
        self.index += 1
