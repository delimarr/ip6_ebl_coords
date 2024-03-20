"""Observer in order to measure trainswitches."""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ebl_coords.backend.command.command import Command, WrapperCommand
from ebl_coords.backend.command.db_cmd import DbCommand
from ebl_coords.backend.observable.gtcommand_subject import GtCommandSubject
from ebl_coords.backend.observable.observer import Observer
from ebl_coords.decorators import override
from ebl_coords.frontend.command.label_cmd import SetTextCmd
from ebl_coords.frontend.command.status_bar_cmd import StatusBarCmd
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem

if TYPE_CHECKING:
    from queue import Queue

    from ebl_coords.frontend.main_gui import Ui_MainWindow


class TsMeasureObserver(Observer):
    """Measure trainswitch observer.

    Args:
        Observer (_type_): observer interface
    """

    def __init__(
        self,
        selected_ts: str,
        gui_queue: Queue[Command],
        worker_queue: Queue[Command],
        ui: Ui_MainWindow,
        points_needed: int = 50,
    ) -> None:
        """Initialize the observer.

        Args:
            selected_ts (str): guid of trainswitch in db.
            gui_queue (Queue[Command]): gui command queue
            worker_queue (Queue[Command]): worker command queue
            ui (Ui_MainWindow): ui
            points_needed (int, optional): How many point should be used for the measurement. Defaults to 50.
        """
        self.subject: GtCommandSubject
        self.selected_ts = selected_ts
        self.gui_queue = gui_queue
        self.worker_queue = worker_queue
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
            self.worker_queue.put(DbCommand(content=cmd))

            self.worker_queue.put(
                WrapperCommand(
                    content=StatusBarCmd(
                        content=f"Weiche bei: ({x}, {y}, {z}) eingemessen.",
                        context=self.ui,
                    ),
                    context=self.gui_queue,
                )
            )
            self.worker_queue.put(
                WrapperCommand(
                    content=SetTextCmd(
                        content=f"({x}, {y}, {z})", context=self.ui.weichen_coord_label
                    ),
                    context=self.gui_queue,
                )
            )
            return
        self.worker_queue.put(
            WrapperCommand(
                content=StatusBarCmd(
                    content=f"Bitte warten. Weiche wird eingemessen: {self.index}/{self.points_needed}",
                    context=self.ui,
                ),
                context=self.gui_queue,
            )
        )
        self.buffer[self.index, :] = self.result
        self.index += 1


class AttachTsMeasureCommand(Command):
    """Create and Attach TsMeasureObserver-Command."""

    def __init__(self, content: tuple[str, Queue[Command], Queue[Command], Ui_MainWindow]) -> None:
        """Create and attach a TsMeasureObserver and set context to GtCommandSubject.

        Args:
            content (Tuple[str, Queue[Command], Queue[Command], Ui_MainWindow]): guid of ts, gui_queue, worker_queue, ui
        """
        super().__init__(content, GtCommandSubject())
        self.context: GtCommandSubject
        self.content: tuple[str, Queue[Command], Queue[Command], Ui_MainWindow]

    @override
    def run(self) -> None:
        """Create and attach a TsMeasureObserver."""
        guid, worker_queue, gui_queue, ui = self.content
        self.context.attach_all_coord(
            TsMeasureObserver(
                selected_ts=guid, gui_queue=gui_queue, worker_queue=worker_queue, ui=ui
            )
        )
