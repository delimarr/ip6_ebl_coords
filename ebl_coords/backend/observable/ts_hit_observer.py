"""Observer in order to detect if trainswitch is occupied."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.gui_cmd import SetComboBoxCommand
from ebl_coords.backend.observable.observer import Observer
from ebl_coords.decorators import override
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem
from ebl_coords.graph_db.graph_db_api import GraphDbApi

if TYPE_CHECKING:
    from queue import Queue

    from ebl_coords.backend.command.base import Command
    from ebl_coords.frontend.main_gui import Ui_MainWindow


class TsHitObserver(Observer):
    """Trainswitch hit observer."""

    def __init__(self, command_queue: Queue[Command], ui: Ui_MainWindow) -> None:
        """Initialize refrence of command queue and ui.

        Args:
            command_queue (Queue[Command]): command queue
            ui (Ui_MainWindow): mainwindow ui
        """
        self.command_queue = command_queue
        self.ui = ui

    @override
    def update(self) -> None:
        """Update QCombobox in map editor."""
        # To Do Ecos abfrage und nächste weiche
        temp_ecos = 0
        weiche = SwitchItem.WEICHE.name
        double_vertex = EdgeRelation.DOUBLE_VERTEX.name
        node_id = self.result[0]
        cmd = f"""
        MATCH(n1:{weiche}{{node_id:'{node_id}'}})-[dv:{double_vertex}]->(n2:{weiche})
        MATCH(n2)-[r]->(t)
        WHERE NOT type(r) = '{double_vertex}'
        RETURN r.edge_id AS edge_id, type(r) AS ts_exit
        """
        graph_db = GraphDbApi()
        df = graph_db.run_query(cmd)

        next_edge_id: str
        # if only one possible exit, take it
        if df.size == 0:
            print("df size 0, ts_hit_observer")
            return
        if df.shape[0] == 1:
            next_edge_id = df.edge_id[0]
        else:
            if temp_ecos == 0:
                next_edge_id = df.loc[df.ts_exit == EdgeRelation.STRAIGHT.name].edge_id[
                    0
                ]
            elif temp_ecos == 1:
                next_edge_id = df.loc[
                    df.ts_exit == EdgeRelation.DEFLECTION.name
                ].edge_id[0]

        self.command_queue.put(
            SetComboBoxCommand(content=next_edge_id, context=self.ui.map_position_CBox)
        )

        print(self.result)
