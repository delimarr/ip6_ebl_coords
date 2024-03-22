"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import Command
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from ebl_coords.frontend.map_editor import MapEditor


class MapAddCustomButtonsToListCmd(Command):
    """Add three custom buttons to map list.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: tuple[str, str, str], context: MapEditor) -> None:
        """Initialize the command.

        Args:
            content (Tuple[str, str, str]): (text, guid_0, guid_1)
            context (MapEditor): map editor
        """
        super().__init__(content, context)
        self.content: tuple[str, str, str]
        self.context: MapEditor

    @override
    def run(self) -> None:
        """Create and add map three buttons."""
        text, guid_0, guid_1 = self.content
        self.context.add_btns_to_list(text=text, guid_0=guid_0, guid_1=guid_1)
