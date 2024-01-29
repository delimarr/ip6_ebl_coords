"""Observer in order to measure trainswitches."""
from __future__ import annotations

from queue import Queue
from typing import TYPE_CHECKING

import numpy as np

from ebl_coords.backend.observable.observer import Observer
from ebl_coords.decorators import override
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem

if TYPE_CHECKING:
    from ebl_coords.backend.command.base import Command
    from ebl_coords.backend.observable.gtcommand_subject import GtCommandSubject


class MeasureTsObserver(Observer):
    """Measure trainswitch observer.

    Args:
        Observer (_type_): observer interface
    """

    def __init__(
        self,
        selected_ts: str,
        gtcommand: GtCommandSubject,
        command_queue: Queue[Command],
        points_needed: int = 150,
    ) -> None:
        """Initialize the observer.

        Args:
            selected_ts (str): guid of trainswitch in db.
            gtcommand (GtCommandSubject): GtCommand Api Subject
            command_queue (Queue[Command]): put command in queue with db and Gui updates.
            points_needed (int, optional): How many point should be used for the measurement. Defaults to 150.
        """
        self.selected_ts = selected_ts
        self.command_queue = command_queue
        self.points_needed = points_needed
        self.buffer = np.empty((points_needed, 3), dtype=np.float32)
        self.index: int = 0
        self.gtcommand = gtcommand
        self.gtcommand.attach(self)

    @override
    def update(self) -> None:
        """Build buffer of coords and put command into queue."""
        if self.index == self.points_needed:
            self.gtcommand.detach(self)
            ts_coord = np.median(self.buffer, axis=0)
            double_vertex = EdgeRelation.DOUBLE_VERTEX.name
            weiche = SwitchItem.WEICHE.name
            cmd = f"""
            MATCH(n1:WEICHE{{node_id:'{self.selected_ts}'}})-[:{double_vertex}]->(n2:{weiche})\
            SET n1.x = '{ts_coord[0]}'\
            SET n2.x = '{ts_coord[0]}'\
            SET n1.y = '{ts_coord[1]}'\
            SET n2.y = '{ts_coord[1]}'\
            SET n1.z = '{ts_coord[2]}'\
            SET n2.z = '{ts_coord[2]}';
            """
            # TO DO put graphcmd into self.command_queue
            print(cmd)
        self.buffer[self.index, :] = self.result
        self.index += 1
