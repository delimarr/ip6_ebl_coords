"""Train switch json class."""
from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(unsafe_hash=True)
class TrainSwitch:
    """Represents a trainswitch for zone."""

    guid: str
    point_in_u: str
    point_in_v: str
    point_straight_u: str
    point_straight_v: str
    point_deflection_u: str
    point_deflection_v: str
