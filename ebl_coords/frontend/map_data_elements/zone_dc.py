"""Map json class."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ebl_coords.frontend.map_data_elements.map_train_switch_dc import MapTsTopopoint


@dataclass(unsafe_hash=True)
class Zone:
    """Represents a zone."""

    name: str
    block_size: int
    width: int
    height: int
    switches: dict[str, MapTsTopopoint]
