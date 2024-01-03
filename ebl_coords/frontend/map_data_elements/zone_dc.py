"""Map json class."""
from dataclasses import dataclass
from typing import Dict

from ebl_coords.frontend.map_data_elements.map_train_switch_dc import MapTrainSwitch


@dataclass(unsafe_hash=True)
class Zone:
    """Represents a zone."""

    name: str
    block_size: int
    width: int
    height: int
    switches: Dict[str, MapTrainSwitch]
