"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import Command
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from ebl_coords.frontend.net_maker import NetMaker


class DrawGridLineCmd(Command):
    """Draw a grid line command.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: tuple[int, int, int, int, bool], context: NetMaker) -> None:
        """Initialize this command.

        Args:
            content (Tuple[int, int, int, int, bool]): (u, v, ut, vt, snap_first)
            context (NetMaker): netmaker
        """
        super().__init__(content, context)
        self.content: tuple[int, int, int, int, bool]
        self.context: NetMaker

    @override
    def run(self) -> None:
        """Draw a grid line."""
        u, v, ut, vt, snap_to_border = self.content
        self.context.draw_grid_line(u, v, ut, vt, snap_first=snap_to_border)
