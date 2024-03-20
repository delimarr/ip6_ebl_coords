"""Strecken Editor."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import WrapperCommand, WrapperFunctionCommand
from ebl_coords.backend.command.db_cmd import DbCommand, FillStreckenCBGuiCommand
from ebl_coords.backend.command.db_cmd import FillStreckenListGuiCommand, StreckenSaveGuiCmd
from ebl_coords.decorators import override
from ebl_coords.frontend.custom_widgets import CustomBtn
from ebl_coords.frontend.editor import Editor
from ebl_coords.graph_db.data_elements.edge_relation_enum import EDGE_RELATION_TO_ENUM
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem

if TYPE_CHECKING:
    from ebl_coords.frontend.gui import Gui


class StreckenEditor(Editor):
    """Editor for train switches.

    Args:
        Editor (_type_): Base Editor class.
    """

    def __init__(self, gui: Gui) -> None:
        """Connect Button events and cache trainswitches.

        Args:
            gui (Gui): gui
        """
        super().__init__(gui)
        self.selected_edge: tuple[str, str] | None = None

        self.ui.strecken_new_btn.clicked.connect(self.reset)
        self.ui.strecken_speichern_btn.clicked.connect(self.save)
        self.ui.strecken_delete_btn.clicked.connect(self.delete_strecke)
        self.reset()

    def _fill_comboboxes(self) -> None:
        self.worker_queue.put(FillStreckenCBGuiCommand(content=self.ui, context=self.gui_queue))

    def _fill_list(self) -> None:
        self.worker_queue.put(
            FillStreckenListGuiCommand(
                content=(self.ui.strecken_list, self.select_strecke),
                context=self.gui_queue,
            )
        )

    def select_strecke(self, custom_btn: CustomBtn) -> None:
        """Select edge from button, does not allow edit or load text."""
        _, relation, _ = custom_btn.button.text().split("\t")
        self.selected_edge = (custom_btn.guid, relation)

    @override
    def reset(self) -> None:
        """Reset all comboboxes and the list."""
        self.ui.strecken_list.clear()
        self._fill_list()
        self._fill_comboboxes()
        self.gui.map_editor.fill_combobox()
        self.gui.map_editor.draw()
        self.selected_edge = None

    @override
    def save(self) -> None:
        """Save a new bi directional connection in the database."""
        self.worker_queue.put(
            StreckenSaveGuiCmd(
                content=(
                    self,
                    self.ui.strecken_comboBox_a.currentText(),
                    self.ui.strecken_comboBox_b.currentText(),
                ),
                context=self.gui_queue,
            )
        )

    def delete_strecke(self) -> None:
        """Delete selected directional edge in the database."""
        if self.selected_edge is not None:
            weiche = SwitchItem.WEICHE.name
            guid, relation = self.selected_edge
            relation = EDGE_RELATION_TO_ENUM[relation].name
            cmd = f"""\
                MATCH (a:{weiche})-[r:{relation}]->(b:{weiche})\
                WHERE r.edge_id = '{guid}'\
                DELETE r;\
            """
            self.worker_queue.put(DbCommand(cmd))
            self.worker_queue.put(
                WrapperCommand(content=WrapperFunctionCommand(self.reset), context=self.gui_queue)
            )
