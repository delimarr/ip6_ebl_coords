"""Output Converter Dataclass."""
from dataclasses import dataclass
from typing import Dict


@dataclass(unsafe_hash=True)
class ConverterOuput:
    """Converter output class."""

    time_stamp: int
    x: float
    y: float
    z: float
    misc: Dict[str, float]
