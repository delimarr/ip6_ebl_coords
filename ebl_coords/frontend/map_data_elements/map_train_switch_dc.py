"""Map Train switch json class."""
from dataclasses import dataclass
from typing import Optional, Tuple

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(unsafe_hash=True)
class MapTsTopopoint:
    """Represents a trainswitch point int the net."""

    name: str
    guid: str
    relation: str
    coords: Optional[Tuple[int, int]] = None
