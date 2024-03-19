"""A Singleton Metaclass."""
from typing import Any, Dict, Type


class SingletonMeta(type):
    """Singleton meta class."""

    _instances: Dict[Type[Any], Any] = {}

    def __call__(cls, *args, **kwargs) -> Any:
        """Return singleton or create if it does not exist yet."""
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
