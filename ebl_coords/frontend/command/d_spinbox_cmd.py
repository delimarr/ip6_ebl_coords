"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import Command
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QDoubleSpinBox


class AddFloatCmd(Command):
    """Add float value to double spinbox.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: float, context: QDoubleSpinBox) -> None:
        """Initialize this command.

        Args:
            content (float): float value to be added
            context (QDoubleSpinBox): double spin box
        """
        super().__init__(content, context)
        self.content: float
        self.context: QDoubleSpinBox

    @override
    def run(self) -> None:
        """Add float value to current value in QDoubleSpinBox."""
        self.context.setValue(self.context.value() + self.content)
