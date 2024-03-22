"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import Command
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from ebl_coords.frontend.main_gui import Ui_MainWindow


class StatusBarCmd(Command):
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
