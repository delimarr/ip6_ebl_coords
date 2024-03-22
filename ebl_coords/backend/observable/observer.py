"""Observer Interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ebl_coords.backend.observable.subject import Subject


class Observer(ABC):
    """Observer interface.

    Args:
        ABC (_type_): Abstract class

    Raises:
        NotImplementedError: interface
    """

    result: Any
    subject: Subject

    @abstractmethod
    def update(self) -> None:
        """Observer update function.

        Raises:
            NotImplementedError: interface
        """
        raise NotImplementedError
