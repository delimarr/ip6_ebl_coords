"""Weichen Editor."""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ebl_coords.backend.observable.ts_measure_observer import TsMeasureObserver
from ebl_coords.decorators import override
from ebl_coords.frontend.custom_widgets import CustomBtn, fill_list
from ebl_coords.frontend.editor import Editor
from ebl_coords.graph_db.data_elements.bpk_enum import Bpk
from ebl_coords.graph_db.data_elements.node_dc import Node
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem
from ebl_coords.graph_db.query_generator import double_node, generate_guid
from ebl_coords.graph_db.query_generator import get_double_nodes, update_double_nodes

if TYPE_CHECKING:
    from ebl_coords.main import MainWindow


class WeichenEditor(Editor):
    """Editor for train switches.

    Args:
        Editor (_type_): Base Editor class.
    """

    def __init__(
        self,
        main_window: MainWindow,
    ) -> None:
        """Connect Buttons.

        Args:
            main_window (MainWindow): main window
        """
        super().__init__(main_window)
        self.strecken_editor = self.main_window.strecken_editor

        self.ui.weichen_new_btn.clicked.connect(self.reset)
        self.ui.weichen_speichern_btn.clicked.connect(self.save)
        self.ui.weichen_einmessen_btn.clicked.connect(self.start_measurement)

        self.selected_ts: str | None = None
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
        ts_number = self.ui.weichen_weichenname_txt.text()
        dcc = self.ui.weichen_dcc_txt.text()
        bpk = self.ui.weichen_bhf_txt.text()
        if bpk and dcc and ts_number:
            node = Node(
                id=generate_guid(),
                ecos_id=dcc,
                switch_item=SwitchItem.WEICHE,
                ts_number=ts_number,
                bpk=Bpk[bpk.upper()],
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
            self.main_window.map_editor.fill_list()
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
        self.ui.weichen_coord_label.setText(
            f"({df['n1.x'][0]}, {df['n1.y'][0]}, {df['n1.z'][0]})"
        )

    def start_measurement(self) -> None:
        """Start measure coordinates for this trainswitch."""
        if self.selected_ts is not None:
            ts_measure_observer = TsMeasureObserver(
                selected_ts=self.selected_ts,
                command_queue=self.main_window.command_queue,
                ui=self.ui,
            )
            self.ui.statusbar.showMessage("Bitte Warten. Weiche wird eingemessen.")
            self.gtcommand.attach(ts_measure_observer)
