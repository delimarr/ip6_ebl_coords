"""Strecken Editor."""
import numpy as np
import pandas as pd

from ebl_coords.decorators import override
from ebl_coords.frontend.custom_widgets import CustomBtn, add_btn_to_list
from ebl_coords.frontend.editor import Editor
from ebl_coords.frontend.main_gui import Ui_MainWindow
from ebl_coords.graph_db.api import Api
from ebl_coords.graph_db.data_elements.bahnhof_enum import Bhf
from ebl_coords.graph_db.data_elements.edge_dc import Edge
from ebl_coords.graph_db.data_elements.edge_relation_enum import EDGE_RELATION_TO_ENUM
from ebl_coords.graph_db.data_elements.edge_relation_enum import TRAINRAILS
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.node_dc import Node
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem
from ebl_coords.graph_db.query_generator import single_edge


class StreckenEditor(Editor):
    """Editor for train switches.

    Args:
        Editor (_type_): Base Editor class.
    """

    def __init__(self, ui: Ui_MainWindow, graph_db: Api) -> None:
        """Bind buttons and fill cache with data from graph db.

        Args:
            ui (Ui_MainWindow): main window
            graph_db (Api): api of graph window
        """
        super().__init__(ui, graph_db)

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
        for relation in EdgeRelation:
            if relation == EdgeRelation.DOUBLE_VERTEX:
                continue
            cmd = f"MATCH (n1)-[:{relation.name}]->(n2) RETURN n1.bhf, n1.name, n1.node_id, n2.bhf, n2.name"
            df = self.graph_db.run_query(cmd)
            if df.size > 0:
                for _, row in df.iterrows():
                    add_btn_to_list(
                        qlist=self.ui.strecken_list,
                        text=f"{row['n1.bhf']}_{row['n1.name']}\t{relation.value}\t{row['n2.bhf']}_{row['n2.name']}",
                        guid=row["n1.node_id"],
                        foo=self.select_strecke,
                    )

    def _get_node(self, bhf: str, name: str, relation: str) -> Node:
        n = self.cache.loc[
            (self.cache["node.bhf"] == bhf)
            & (self.cache["node.name"] == name)
            & (self.cache.exit == relation)
        ].iloc[0, :]
        return Node(
            id=n["node.node_id"],
            ecos_id="",
            switch_item=SwitchItem.WEICHE,
            name=n["node.name"],
            bhf=Bhf[bhf],
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

    @override
    def save(self) -> None:
        """Save a new bi directional connection in the database."""
        bhf1, name1, relation1 = self.ui.strecken_comboBox_a.currentText().split("\t")
        bhf2, name2, relation2 = self.ui.strecken_comboBox_b.currentText().split("\t")
        n1 = self._get_node(bhf1, name1, relation1)
        n2 = self._get_node(bhf2, name2, relation2)
        edge1 = Edge(
            source=n1, dest=n2, relation=EDGE_RELATION_TO_ENUM[relation1], distance=0
        )
        edge2 = Edge(
            source=n2, dest=n1, relation=EDGE_RELATION_TO_ENUM[relation2], distance=0
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
            WHERE a.node_id = '{custom_btn.guid}'\
            DELETE r;\
        """
        self.graph_db.run_query(cmd)
        self.reset()
