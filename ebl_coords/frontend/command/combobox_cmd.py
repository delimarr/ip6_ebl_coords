"""Command pattern Gui."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import Command
from ebl_coords.decorators import override

if TYPE_CHECKING:
    import pandas as pd
    from PyQt6.QtWidgets import QComboBox


class SetComboBoxCmd(Command):
    """Select a new element in a QComboBox.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: str, context: QComboBox) -> None:
        """Initialize userdata and QCombobox.

        Args:
            content (str): UserData of QCombobox-Item
            context (QComboBox): QCombobox
        """
        super().__init__(content, context)
        self.content: str
        self.context: QComboBox

    @override
    def run(self) -> None:
        """Match content to UserData from QComboBox element and select it."""
        for i in range(self.context.count()):
            if self.context.itemData(i) == self.content:
                self.context.setCurrentIndex(i)
                return


class SetComboBoxContentCmd(Command):
    """Replace ComboBocx content.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: pd.Series, context: QComboBox) -> None:
        """Initialize this command.

        Args:
            content (pd.Series): Series containing all element texts.
            context (QComboBox): container
        """
        super().__init__(content, context)
        self.content: pd.Series
        self.context: QComboBox

    @override
    def run(self) -> None:
        """Clear and add all elements."""
        self.context.clear()
        self.context.addItems(self.content)


class AddComboBoxElementCmd(Command):
    """Add a single element to a combobox with data.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: tuple[str, str], context: QComboBox) -> None:
        """Initialize this command.

        Args:
            content (Tuple[str, str]): (name, data)
            context (QComboBox): combo box
        """
        super().__init__(content, context)
        self.content: tuple[str, str]
        self.context: QComboBox

    @override
    def run(self) -> None:
        """Add a single combo box element with its data to container."""
        self.context.addItem(self.content[1], self.content[0])
