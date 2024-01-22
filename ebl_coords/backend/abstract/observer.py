"""Observer interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class Observer(ABC):
    """Observer interface.

    Args:
        ABC (_type_): abstract class

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
