"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.base import Command
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QLabel

    from ebl_coords.frontend.main_gui import Ui_MainWindow


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
