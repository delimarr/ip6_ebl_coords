"""Base Command. Command-Pattern."""
from abc import ABC, abstractmethod
from queue import Queue
from typing import Any, Callable, Optional

from ebl_coords.decorators import override


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


class WrapperCommand(Command):
    """A Wrapper Command, in order to a command directly to the next queue.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: Command, context: Queue[Command]) -> None:
        """Initialize this command.

        Args:
            content (Command): gui command
            context (Queue[Command]): gui_queue
        """
        super().__init__(content, context)
        self.content: Command
        self.context: Queue[Command]

    @override
    def run(self) -> None:
        """Put the command in the context queue."""
        self.context.put(self.content)


class WrapperFunctionCommand(Command):
    """A Wrapper Command, in order to execute function as run.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: Callable[..., Any]) -> None:
        """Initialize this command.

        Args:
            content (Callable[..., Any]): any function
        """
        super().__init__(content, None)
        self.content: Callable[..., Any]

    @override
    def run(self) -> None:
        """Put the command in the context queue."""
        self.content()
