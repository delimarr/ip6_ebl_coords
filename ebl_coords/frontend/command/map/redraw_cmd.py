"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import Command
from ebl_coords.backend.command.db_cmd import MapDrawOccupiedGuiCmd
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from queue import Queue

    from ebl_coords.frontend.map_editor import MapEditor


class RedrawCmd(Command):
    """Redraw the complete map_label.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: tuple[MapEditor, Queue[Command]], context: Queue[Command]) -> None:
        """Initialize this command.

        Args:
            content (Tuple[MapEditor, Queue[Command]]): (map_editor, gui_queue)
            context (Queue[Command]): worker_queue
        """
        super().__init__(content, context)
        self.content: tuple[MapEditor, Queue[Command]]
        self.context: Queue[Command]

    @override
    def run(self) -> None:
        """Redraw the map_label."""
        map_editor, gui_queue = self.content
        edge_id = map_editor.ui.map_position_CBox.currentData()
        self.context.put(
            MapDrawOccupiedGuiCmd(
                content=(edge_id, map_editor, map_editor.ui.map_distance_dsb.value()),
                context=gui_queue,
            )
        )
