"""Base Command. Command-Pattern."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ebl_coords.main import MainWindow


class Command(ABC):
    """Base Command Interface.

    Args:
        ABC (_type_): Abstract class

    Raises:
        NotImplementedError: interface
    """

    def __init__(self, main_window: MainWindow) -> None:
        """Initialize Command with main_window as context.

        Args:
            main_window (MainWindow): main_window
        """
        self.main_window = main_window

    @abstractmethod
    def run(self) -> None:
        """Execute this command.

        Raises:
            NotImplementedError: interface
        """
        raise NotImplementedError
