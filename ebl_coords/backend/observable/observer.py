"""Observer Interface."""
from abc import ABC, abstractmethod
from typing import Any


class Observer(ABC):
    """Observer interface.

    Args:
        ABC (_type_): Abstract class

    Raises:
        NotImplementedError: interface
    """

    result: Any

    @abstractmethod
    def update(self) -> None:
        """Observer update function.

        Raises:
            NotImplementedError: interface
        """
        raise NotImplementedError
