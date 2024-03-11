"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from ebl_coords.backend.command.base import Command
from ebl_coords.backend.constants import OCCUPIED_HEX
from ebl_coords.decorators import override
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QComboBox, QDoubleSpinBox, QLabel

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


class SetFloatCommand(Command):
    """Set a float value in a QDoubleSpinBox."""

    def __init__(self, content: float, context: QDoubleSpinBox) -> None:
        """Initialize with float and container.

        Args:
            content (float): QDoubleSpinBox
            context (QDoubleSpinBox): new float value
        """
        super().__init__(content, context)
        self.content: float
        self.context: QDoubleSpinBox

    def run(self) -> None:
        """Set the float value."""
        self.context.setValue(self.content)


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


class AddFloatCommand(Command):
    """Add Float Value Command.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: float, context: QDoubleSpinBox) -> None:
        """Initialize with float and conatiner.

        Args:
            content (float): float value to be added
            context (QDoubleSpinBox): container
        """
        super().__init__(content, context)
        self.content: float
        self.context: QDoubleSpinBox

    @override
    def run(self) -> None:
        """Add the float value."""
        old_value = self.context.value()
        self.context.setValue(old_value + self.content)


class UpdateMapCommand(Command):
    """Redraw the map command.

    Args:
        Command (_type_): interface
    """

    def __init__(self, context: MapEditor) -> None:
        """Initialize with MapEditor.

        Args:
            context (MapEditor): mapeditor
        """
        super().__init__(None, context)
        self.context: MapEditor

    @override
    def run(self) -> None:
        """Redraw the map."""
        self.context.map_pos_changed()


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

    def __init__(self, content: dict[str, Any], context: MapEditor) -> None:
        """Initialize this command.

        Args:
            content (pd.DataFrame): Dataframe containing information occupied edge.
            context (MapEditor): map editor
        """
        super().__init__(content, context)
        self.content: dict[str, Any]
        self.context: MapEditor
        self.switches = self.context.zone.switches
        self.ecos_df = self.context.main_window.ecos_df
        self.occupied_width: int = 13

    @override
    def run(self) -> None:
        """Draw line over occupied edge."""
        points: list[tuple[int, int]] = []
        source_id = self.content["source_id"]
        dest_id = self.content["dest_id"]

        neutral_string = EdgeRelation.NEUTRAL.name

        # neutral point source
        coords = self.switches[f"{source_id[:-1]}0{neutral_string}"].coords
        if coords is None:
            return
        points.append(coords)

        # maybe straight/deflection point source
        ts_source = self.content["ts_source"]
        if ts_source != neutral_string:
            coords = self.switches[source_id + ts_source].coords
            if coords is None:
                return
            points.append(coords)

        # maybe straight/deflection point dest
        ts_dest = self.content["ts_dest"]
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
        points_array: np.ndarray = np.array(points)

        lengths = np.apply_along_axis(
            np.linalg.norm, axis=1, arr=points_array[1:, :] - points_array[:-1, :]
        )
        occupied_length = self.content["occupied_percent"] * lengths.sum()
        self.context.net_maker.clear()
        for i in range(lengths.size):
            length = lengths[i]
            p1 = points_array[i]
            p2 = points_array[i + 1]

            if occupied_length >= length:
                self.context.net_maker.draw_grid_line(
                    p2[0],
                    p2[1],
                    p1[0],
                    p1[1],
                    snap_first=False,
                    snap_second=False,
                    color=OCCUPIED_HEX,
                    width=self.occupied_width,
                )

            else:
                direction = (p2 - p1) / length
                train_position = p1 + occupied_length * direction
                self.context.net_maker.draw_grid_line(
                    p1[0],
                    p1[1],
                    train_position[0],
                    train_position[1],
                    snap_first=False,
                    snap_second=False,
                    color=OCCUPIED_HEX,
                    width=self.occupied_width,
                )
                break
            occupied_length -= length
        self.context.draw()
