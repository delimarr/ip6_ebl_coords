"""Redraw Net Command."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.base import Command

if TYPE_CHECKING:
    from ebl_coords.frontend.map_editor import MapEditor


class RedrawCommand(Command):
    """Redraw Net Command, need refactoring."""

    def __init__(self, context: MapEditor) -> None:
        """Initialize Redraw Command.

        Args:
            context (MapEditor): map editor
        """
        super().__init__(content=None, context=context)
        self.context: MapEditor

    def run(self) -> None:
        """Redraw Net."""
        self.context.net_maker.clear()
        self.context.draw()
        self.context.map_pos_changed()
