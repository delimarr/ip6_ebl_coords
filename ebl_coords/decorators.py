"""Override Decorator."""
from typing import Callable, TypeVar

# Create a type variable to represent any type of callable function/method
T = TypeVar("T", bound=Callable[..., object])


def override(method: T) -> T:
    """Decorator to indicate that the decorated method overrides a method in the superclass."""
    return method
