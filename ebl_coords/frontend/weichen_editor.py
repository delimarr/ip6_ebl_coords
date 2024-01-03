"""Weichen Editor."""
from typing import List, Optional

import numpy as np

from ebl_coords.backend.converter.helpers import guid
from ebl_coords.backend.gtcommand.api import GtCommandApi
from ebl_coords.decorators import override
from ebl_coords.frontend.custom_widgets import CustomBtn, fill_list
from ebl_coords.frontend.editor import Editor
from ebl_coords.frontend.main_gui import Ui_MainWindow
from ebl_coords.frontend.strecken_editor import StreckenEditor
from ebl_coords.graph_db.api import Api
from ebl_coords.graph_db.data_elements.bahnhof_enum import Bhf
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.node_dc import Node
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem
from ebl_coords.graph_db.query_generator import double_node, get_double_nodes
from ebl_coords.graph_db.query_generator import update_double_nodes


class WeichenEditor(Editor):
    """Editor for train switches.

    Args:
        Editor (_type_): Base Editor class.
    """

    def __init__(
        self, ui: Ui_MainWindow, graph_db: Api, strecken_editor: StreckenEditor
    ) -> None:
        """Bind buttons and fill list with data from the db.

        Args:
            ui (Ui_MainWindow): main window
            graph_db (Api): api of graph database
            strecken_editor (StreckenEditor): invokes reset of strecken_editor, if trainswitches change.
        """
        super().__init__(ui=ui, graph_db=graph_db)
        self.strecken_editor = strecken_editor
        self.gt_api = GtCommandApi()

        self.ui.weichen_new_btn.clicked.connect(self.reset)
        self.ui.weichen_speichern_btn.clicked.connect(self.save)
        self.ui.weichen_einmessen_btn.clicked.connect(self.start_measurement)

        self.selected_ts: Optional[str] = None
        self.reset()

    @override
    def reset(self) -> None:
        """Clear all textfields and deselect the active trainswitch."""
        self.ui.weichen_weichenname_txt.clear()
        self.ui.weichen_dcc_txt.clear()
        self.ui.weichen_bhf_txt.clear()
        self.ui.weichen_list.clear()
        fill_list(self.graph_db, self.ui.weichen_list, self.select_ts)
        self.selected_ts = None
        self.strecken_editor.reset()

    @override
    def save(self) -> None:
        """Save a new trainswitch in the database and reset the editor."""
        name = self.ui.weichen_weichenname_txt.text()
        dcc = self.ui.weichen_dcc_txt.text()
        bhf = self.ui.weichen_bhf_txt.text()
        if bhf and dcc and name:
            node = Node(
                id=guid(),
                ecos_id=dcc,
                switch_item=SwitchItem.WEICHE,
                name=name,
                bhf=Bhf[bhf.upper()],
                coords=np.zeros((3,), dtype=int),
            )
            if self.selected_ts is None:
                # create new double node
                cmd, _ = double_node(node)
            else:
                # modify existing double node
                node.id = self.selected_ts
                cmd = update_double_nodes(node)
            self.graph_db.run_query(cmd)
            self.reset()

    def select_ts(self, custom_btn: CustomBtn) -> None:
        """Select a train switch.

        Args:
            custom_btn (CustomBtn): source button
        """
        self.selected_ts = custom_btn.guid
        cmd = get_double_nodes(self.selected_ts)
        df = self.graph_db.run_query(cmd)
        self.ui.weichen_bhf_txt.setText(df["n1.bhf"][0])
        self.ui.weichen_dcc_txt.setText(df["n1.ecos_id"][0])
        self.ui.weichen_weichenname_txt.setText(df["n1.name"][0])

    def start_measurement(self) -> None:
        """Start measure coordinates for this trainswitch."""
        if self.selected_ts is not None:
            self.gt_api.start_record()
            coords: List[np.ndarray] = []
            while len(coords) < 150:
                if self.gt_api.buffer.not_empty:
                    coords.append(self.gt_api.buffer.get())
            self.gt_api = GtCommandApi()
            coords = np.array(coords, dtype=np.float32)
            ts_coord = np.median(coords, axis=0)
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
            self.graph_db.run_query(cmd)
            print(ts_coord)
        else:
            print("pls select first an existing trainswitch")
