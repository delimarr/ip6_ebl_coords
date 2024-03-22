"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import Command
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from ebl_coords.frontend.map_editor import MapEditor


class ClearCmd(Command):
    """Clear the map.

    Args:
        Command (_type_): interface
    """

    def __init__(self, context: MapEditor) -> None:
        """Initialize this command.

        Args:
            context (MapEditor): map_editor
        """
        super().__init__(None, context)
        self.context: MapEditor

    @override
    def run(self) -> None:
        """Clear the map_label."""
        self.context.net_maker.clear()
