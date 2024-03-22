"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import Command
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from ebl_coords.frontend.strecken_editor import StreckenEditor


class StreckenResetCmd(Command):
    """Reset the StreckenEditor."""

    def __init__(self, context: StreckenEditor) -> None:
        """Initialize this Command.

        Args:
            context (StreckenEditor): strecken_editor
        """
        super().__init__(None, context)
        self.context: StreckenEditor

    @override
    def run(self) -> None:
        """Reset all fields from strecken_editor."""
        self.context.reset()
