"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PyQt6.QtWidgets import QListWidgetItem

from ebl_coords.backend.command.command import Command
from ebl_coords.decorators import override
from ebl_coords.frontend.custom_widgets import CustomBtn

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QListWidget


class AddCustomButtonToListCmd(Command):
    """Add CustomButton to a QList command.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: dict[str, Any], context: QListWidget) -> None:
        """Create and add Custom Button to list widget.

        Args:
            content (Dict[str, Any]): {"callable" : Callable, "guid" : str, "text" : str}
            context (QListWidget): QListWidget
        """
        super().__init__(content, context)
        self.context: QListWidget
        self.content: dict[str, Any]

    @override
    def run(self) -> None:
        """Create a custom button, add it to QList and connect to it foo."""
        item = QListWidgetItem(self.context)
        custom_btn = CustomBtn(self.content["text"], self.content["guid"])
        custom_btn.button.released.connect(lambda: self.content["callable"](custom_btn))
        item.setSizeHint(custom_btn.sizeHint())
        self.context.setItemWidget(item, custom_btn)
