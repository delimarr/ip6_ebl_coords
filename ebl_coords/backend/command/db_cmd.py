"""Command pattern Graph Db."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from ebl_coords.backend.command.base import Command
from ebl_coords.backend.command.gui_cmd import SetComboBoxCommand
from ebl_coords.decorators import override
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem
from ebl_coords.graph_db.graph_db_api import GraphDbApi

if TYPE_CHECKING:
    from ebl_coords.frontend.map_editor import MapEditor


class DbCommand(Command):
    """Command pattern.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: str) -> None:
        """Initialize command with query.

        Args:
            content (str): query call
        """
        super().__init__(content)
        self.context: GraphDbApi = GraphDbApi()

    @override
    def run(self) -> None:
        """Execute query."""
        self.context.run_query(self.content)


class OccupyNextEdgeCommand(Command):
    """Get next edge to occupy."""

    def __init__(self, content: tuple[str, pd.DataFrame], context: MapEditor) -> None:
        """Initialize occupy command.

        Args:
            content (tuple[str, pd.DataFrame]): source node_id, ecos Dataframe
            context (MapEditor): map editor
        """
        super().__init__(content, context)
        self.content: tuple[str, pd.DataFrame]
        self.context: MapEditor
        self.graph_db = GraphDbApi()
        self.node_id, self.ecos_df = self.content
        self.command_queue = self.context.main_window.command_queue

    @override
    def run(self) -> None:
        """Get next edge and update QCombobox."""
        weiche = SwitchItem.WEICHE.name
        double_vertex = EdgeRelation.DOUBLE_VERTEX.name

        relation = EdgeRelation.NEUTRAL.name

        if self.node_id[-1] == "0":
            neutral_node_id = f"{self.node_id[:-1]}0"
            state = self.ecos_df.loc[self.ecos_df.guid == neutral_node_id].state.iloc[0]
            state = int(state)
            assert state in (0, 1)
            if state == 0:
                relation = EdgeRelation.STRAIGHT.name
            else:
                relation = EdgeRelation.DEFLECTION.name

        cmd = f"""
        MATCH(n1:{weiche}{{node_id:'{self.node_id}'}})-[dv:{double_vertex}]->(n2:{weiche})
        MATCH(n2)-[r:{relation}]->(t)
        RETURN r.edge_id AS edge_id
        """
        df = self.graph_db.run_query(cmd)
        assert df.shape[0] <= 1
        if df.shape[0] == 1:
            next_edge_id = df.edge_id.iloc[0]

            self.command_queue.put(
                SetComboBoxCommand(
                    content=next_edge_id, context=self.context.ui.map_position_CBox
                )
            )
