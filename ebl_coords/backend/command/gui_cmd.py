"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from ebl_coords.backend.command.base import Command
from ebl_coords.backend.constants import OCCUPIED_HEX
from ebl_coords.decorators import override
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QComboBox, QLabel

    from ebl_coords.frontend.main_gui import Ui_MainWindow
    from ebl_coords.frontend.map_editor import MapEditor


class StatusBarCommand(Command):
    """Display StatusBar.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: str, context: Ui_MainWindow) -> None:
        """Initialize command.

        Args:
            content (str): message to be displayed
            context (Ui_MainWindow): Ui Container
        """
        super().__init__(content, context)
        self.content: str
        self.context: Ui_MainWindow

    @override
    def run(self) -> None:
        """Display message in statusbar."""
        self.context.statusbar.showMessage(self.content)


class SetTextCommand(Command):
    """Update a QLabel text.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: str, context: QLabel) -> None:
        """Initialize context and content.

        Args:
            content (str): new text
            context (QLabel): target QLabel
        """
        super().__init__(content, context)
        self.content: str
        self.context: QLabel

    @override
    def run(self) -> None:
        """Update text."""
        self.context.setText(self.content)


class SetComboBoxCommand(Command):
    """Select a new element in a QComboBox."""

    def __init__(self, content: str, context: QComboBox) -> None:
        """Initialize userdata and QCombobox.

        Args:
            content (str): UserData of QCombobox-Item
            context (QComboBox): QCombobox
        """
        super().__init__(content, context)
        self.content: str
        self.context: QComboBox

    @override
    def run(self) -> None:
        """Match content to UserData from QComboBox element and select it."""
        for i in range(self.context.count()):
            if self.context.itemData(i) == self.content:
                self.context.setCurrentIndex(i)
                return


class DrawOccupiedNetCommand(Command):
    """Redraw the net and color occupied edge."""

    def __init__(self, content: pd.DataFrame, context: MapEditor) -> None:
        """Initialize this command.

        Args:
            content (pd.DataFrame): Dataframe containing information occupied edge.
            context (MapEditor): map editor
        """
        super().__init__(content, context)
        self.content: pd.DataFrame
        self.context: MapEditor
        self.switches = self.context.zone.switches
        self.ecos_df = self.context.main_window.ecos_df

    @override
    def run(self) -> None:
        """Draw line over occupied edge."""
        points: list[tuple[int, int]] = []
        source_id = self.content.source_id.iloc[0]
        dest_id = self.content.dest_id.iloc[0]

        neutral_string = EdgeRelation.NEUTRAL.name

        # neutral point source
        coords = self.switches[f"{source_id[:-1]}0{neutral_string}"].coords
        if coords is None:
            return
        points.append(coords)

        # maybe straight/deflection point source
        ts_source = self.content.ts_source.iloc[0]
        if ts_source != neutral_string:
            coords = self.switches[source_id + ts_source].coords
            if coords is None:
                return
            points.append(coords)

        # maybe straight/deflection point dest
        ts_dest = self.content.ts_dest.iloc[0]
        if ts_dest != neutral_string:
            coords = self.switches[dest_id + ts_dest].coords
            if coords is None:
                return
            points.append(coords)

        # neutral point dest
        coords = self.switches[f"{dest_id[:-1]}0{neutral_string}"].coords
        if coords is None:
            return
        points.append(coords)

        self.context.net_maker.clear()
        self.context.draw()
        for i in range(len(points) - 1):
            p1: tuple[int, int] = points[i]
            p2: tuple[int, int] = points[i + 1]

            self.context.net_maker.draw_grid_line(
                p2[0],
                p2[1],
                p1[0],
                p1[1],
                snap_first=True,
                snap_second=True,
                color=OCCUPIED_HEX,
            )
