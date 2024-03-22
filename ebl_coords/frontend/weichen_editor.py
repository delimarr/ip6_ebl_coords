"""Weichen Editor."""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ebl_coords.backend.command.command import WrapperCommand, WrapperFunctionCommand
from ebl_coords.backend.command.db_cmd import DbCommand, FillTsListGuiCommand, GetTsGuiCommand
from ebl_coords.backend.command.ecos_cmd import UpdateEocsDfCommand
from ebl_coords.backend.observable.ts_measure_observer import AttachTsMeasureCommand
from ebl_coords.decorators import override
from ebl_coords.frontend.custom_widgets import CustomBtn
from ebl_coords.frontend.editor import Editor
from ebl_coords.graph_db.data_elements.bpk_enum import Bpk
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.node_dc import Node
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem
from ebl_coords.graph_db.query_generator import double_node, generate_guid, update_double_nodes

if TYPE_CHECKING:
    from ebl_coords.frontend.gui import Gui


class WeichenEditor(Editor):
    """Editor for train switches.

    Args:
        Editor (_type_): interface
    """

    def __init__(
        self,
        gui: Gui,
    ) -> None:
        """Initialize weichen_editor for main gui.

        Args:
            gui (Gui): gui
        """
        super().__init__(gui)
        self.strecken_editor = self.gui.strecken_editor

        self.ui.weichen_new_btn.clicked.connect(self.reset)
        self.ui.weichen_speichern_btn.clicked.connect(self.save)
        self.ui.weichen_einmessen_btn.clicked.connect(self.start_measurement)
        self.ui.weichen_delete_btn.clicked.connect(self.delete_ts)

        self.selected_ts: str | None = None
        self.reset()

    @override
    def reset(self) -> None:
        """Clear all textfields and deselect the active trainswitch."""
        self.ui.weichen_weichenname_txt.clear()
        self.ui.weichen_dcc_txt.clear()
        self.ui.weichen_bhf_txt.clear()
        self.ui.weichen_list.clear()
        self.selected_ts = None
        self.worker_queue.put(
            FillTsListGuiCommand(
                content=(self.ui.weichen_list, self.select_ts), context=self.gui_queue
            )
        )

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
            self.worker_queue.put(DbCommand(cmd))
            self.worker_queue.put(UpdateEocsDfCommand(self.gui.ebl_coords))
            self.gui.map_editor.fill_list()
            self.reset()
            self.strecken_editor.reset()

    def select_ts(self, custom_btn: CustomBtn) -> None:
        """Select a train switch.

        Args:
            custom_btn (CustomBtn): source button
        """
        self.selected_ts = custom_btn.guid
        self.worker_queue.put(
            GetTsGuiCommand(content=(self.selected_ts, self.gui.ui), context=self.gui_queue)
        )

    def delete_ts(self) -> None:
        """Delete selected trainswitch and all attached edges."""
        if self.selected_ts is not None:
            double_vertex = EdgeRelation.DOUBLE_VERTEX.name
            weiche = SwitchItem.WEICHE.name
            db_call = f"""
            MATCH(n1:{weiche}{{node_id:'{self.selected_ts}'}})-[:{double_vertex}]->(n2:{weiche}) DETACH DELETE n1, n2;
            """
            self.worker_queue.put(DbCommand(content=db_call))
            self.worker_queue.put(
                WrapperCommand(content=WrapperFunctionCommand(self.reset), context=self.gui_queue)
            )
            self.worker_queue.put(
                WrapperCommand(
                    content=WrapperFunctionCommand(self.gui.map_editor.reset),
                    context=self.gui_queue,
                )
            )
            self.worker_queue.put(
                WrapperCommand(
                    content=WrapperFunctionCommand(self.strecken_editor.reset),
                    context=self.gui_queue,
                )
            )

    def start_measurement(self) -> None:
        """Start measure coordinates for this trainswitch."""
        if self.selected_ts is not None:
            self.worker_queue.put(
                AttachTsMeasureCommand(
                    content=(
                        self.selected_ts,
                        self.gui_queue,
                        self.worker_queue,
                        self.gui.ui,
                    ),
                )
            )
