"""Map json class."""
from dataclasses import dataclass, field
from typing import List

from dataclasses_json import dataclass_json

from ebl_coords.frontend.map_data_elements.train_switch_dc import TrainSwitch


@dataclass_json
@dataclass(unsafe_hash=True)
class Zone:
    """Represents a zone."""

    name: str
    width: int
    height: int
    keys_width: List[str] = field(default_factory=list)
    keys_height: List[str] = field(default_factory=list)
    switches: List[TrainSwitch] = field(default_factory=list)
