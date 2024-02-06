"""Strecken Editor."""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from ebl_coords.decorators import override
from ebl_coords.frontend.custom_widgets import CustomBtn, add_btn_to_list
from ebl_coords.frontend.editor import Editor
from ebl_coords.graph_db.data_elements.bpk_enum import Bpk
from ebl_coords.graph_db.data_elements.edge_dc import Edge
from ebl_coords.graph_db.data_elements.edge_relation_enum import EDGE_RELATION_TO_ENUM
from ebl_coords.graph_db.data_elements.edge_relation_enum import TRAINRAILS
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.node_dc import Node
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem
from ebl_coords.graph_db.query_generator import generate_guid, single_edge

if TYPE_CHECKING:
    from ebl_coords.main import MainWindow


class StreckenEditor(Editor):
    """Editor for train switches.

    Args:
        Editor (_type_): Base Editor class.
    """

    def __init__(self, main_window: MainWindow) -> None:
        """Connect Button events and cache trainswitches.

        Args:
            main_window (MainWindow): main_window
        """
        super().__init__(main_window)

        self.ui.strecken_new_btn.clicked.connect(self.reset)
        self.ui.strecken_speichern_btn.clicked.connect(self.save)

        self.cache: pd.DataFrame
        self._build_cache()

    def _build_cache(self) -> None:
        cmd = "MATCH (node:WEICHE) RETURN node.bhf, node.name, node.node_id"
        self.cache = self.graph_db.run_query(cmd)[::2]
        shape = self.cache.shape[0]
        self.cache = pd.concat([self.cache] * 3, ignore_index=True)
        exits = TRAINRAILS * shape
        exits.sort()
        self.cache.insert(self.cache.shape[1], "exit", exits)
        mask = self.cache.exit != EdgeRelation.NEUTRAL.value
        self.cache.loc[mask, "node.node_id"] = self.cache[mask]["node.node_id"].apply(
            lambda x: x[:-1] + "1"
        )
        self.cache.sort_values(by=["node.bhf", "node.name"], inplace=True)

    def _fill_comboboxes(self) -> None:
        items = (
            self.cache["node.bhf"]
            + "\t"
            + self.cache["node.name"]
            + "\t"
            + self.cache.exit
        )
        self.ui.strecken_comboBox_a.addItems(items)
        self.ui.strecken_comboBox_b.addItems(items)

    def _fill_list(self) -> None:
        for guid, edge in self.graph_db.edges_tostring():
            add_btn_to_list(
                qlist=self.ui.strecken_list,
                text=edge,
                guid=guid,
                foo=self.select_strecke,
            )

    def _get_node(self, bpk: str, ts_number: str, relation: str) -> Node:
        n = self.cache.loc[
            (self.cache["node.bhf"] == bpk)
            & (self.cache["node.name"] == ts_number)
            & (self.cache.exit == relation)
        ].iloc[0, :]
        return Node(
            id=n["node.node_id"],
            ecos_id="",
            switch_item=SwitchItem.WEICHE,
            ts_number=n["node.name"],
            bpk=Bpk[bpk],
            coords=np.zeros((3,)),
        )

    @override
    def reset(self) -> None:
        """Reset all comboboxes and the list."""
        self._build_cache()
        self.ui.strecken_comboBox_a.clear()
        self.ui.strecken_comboBox_b.clear()
        self.ui.strecken_list.clear()
        self._fill_list()
        self._fill_comboboxes()
        self.main_window.map_editor.fill_combobox()

    @override
    def save(self) -> None:
        """Save a new bi directional connection in the database."""
        bhf1, name1, relation1 = self.ui.strecken_comboBox_a.currentText().split("\t")
        bhf2, name2, relation2 = self.ui.strecken_comboBox_b.currentText().split("\t")
        n1 = self._get_node(bhf1, name1, relation1)
        n2 = self._get_node(bhf2, name2, relation2)
        guid = generate_guid()
        edge1 = Edge(
            id=f"{guid}_0",
            source=n1,
            dest=n2,
            relation=EDGE_RELATION_TO_ENUM[relation1],
            target=EDGE_RELATION_TO_ENUM[relation2],
            distance=0,
        )
        edge2 = Edge(
            id=f"{guid}_1",
            source=n2,
            dest=n1,
            relation=EDGE_RELATION_TO_ENUM[relation2],
            target=EDGE_RELATION_TO_ENUM[relation1],
            distance=0,
        )
        cmd = single_edge(edge1)
        self.graph_db.run_query(cmd)
        cmd = single_edge(edge2)
        self.graph_db.run_query(cmd)
        self.reset()

    def select_strecke(self, custom_btn: CustomBtn) -> None:
        """Delete a directional edge in the database.

        Args:
            custom_btn (CustomBtn): Button clicked
        """
        weiche = SwitchItem.WEICHE.name
        _, relation, _ = custom_btn.button.text().split("\t")
        relation = EDGE_RELATION_TO_ENUM[relation].name
        cmd = f"""\
            MATCH (a:{weiche})-[r:{relation}]->(b:{weiche})\
            WHERE r.edge_id = '{custom_btn.guid}'\
            DELETE r;\
        """
        self.graph_db.run_query(cmd)
        self.reset()
