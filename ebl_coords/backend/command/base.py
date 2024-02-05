"""Base Command. Command-Pattern."""
from abc import ABC, abstractmethod
from typing import Any, Optional


class Command(ABC):
    """Base Command Interface.

    Args:
        ABC (_type_): Abstract class

    Raises:
        NotImplementedError: interface
    """

    def __init__(self, content: Any, context: Optional[Any] = None) -> None:
        """Initialize Command.

        Args:
            content (Any): New content.
            context (Optional[Any], optional): Object to be worked on. Defaults to None.
        """
        self.context = context
        self.content = content

    @abstractmethod
    def run(self) -> None:
        """Execute this command.

        Raises:
            NotImplementedError: interface
        """
        raise NotImplementedError
