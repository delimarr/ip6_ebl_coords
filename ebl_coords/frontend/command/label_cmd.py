"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import Command
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QLabel


class SetTextCmd(Command):
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
