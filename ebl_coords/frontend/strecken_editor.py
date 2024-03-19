"""Strecken Editor."""
from __future__ import annotations

from typing import TYPE_CHECKING

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

        self.ui.strecken_new_btn.clicked.connect(self.reset)
        self.ui.strecken_speichern_btn.clicked.connect(self.save)
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

    @override
    def reset(self) -> None:
        """Reset all comboboxes and the list."""
        self.ui.strecken_list.clear()
        self._fill_list()
        self._fill_comboboxes()
        self.gui.map_editor.fill_combobox()
        self.gui.map_editor.draw()

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
        self.worker_queue.put(DbCommand(cmd))
        self.reset()
