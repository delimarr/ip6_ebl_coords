"""Subject interface."""
from __future__ import annotations

from abc import abstractmethod
from threading import RLock
from typing import TYPE_CHECKING, Any

from ebl_coords.backend.singleton_meta import SingletonMeta

if TYPE_CHECKING:
    from ebl_coords.backend.observable.observer import Observer


class Subject(metaclass=SingletonMeta):
    """Subject interface.

    Args:
        ABC (_type_): abstract class

    Raises:
        NotImplementedError: interface
        NotImplementedError: interface
    """

    @abstractmethod
    def __init__(self) -> None:
        """Initialize the Subject with reentry lock."""
        self.lock = RLock()

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """Attach observer to subject.

        Args:
            observer (Observer): observer

        Raises:
            NotImplementedError: interface
        """
        raise NotImplementedError

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """Detach observer from subject.

        Args:
            observer (Observer): observer

        Raises:
            NotImplementedError: interface
        """
        raise NotImplementedError

    def notify(self, observers: list[Observer], result: Any) -> None:
        """Notify observers in list and set result.

        Args:
            observers (list[Observer]): list of observers
            result (Any): result
        """
        with self.lock:
            for observer in observers:
                observer.result = result
                observer.update()
