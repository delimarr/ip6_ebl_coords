"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from ebl_coords.backend.command.command import Command
from ebl_coords.backend.constants import OCCUPIED_HEX
from ebl_coords.decorators import override
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation

if TYPE_CHECKING:
    from ebl_coords.frontend.map_editor import MapEditor


class DrawOccupiedNetCmd(Command):
    """Redraw the net and color occupied edge.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: dict[str, Any], context: MapEditor) -> None:
        """Initialize this command.

        Args:
            content (dict[str, Any]): _description_
            context (MapEditor): map editor
        """
        super().__init__(content, context)
        self.content: dict[str, Any]
        self.context: MapEditor
        self.switches = self.context.zone.switches
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
