"""Neo4j node."""
from dataclasses import dataclass

import numpy as np

from ebl_coords.graph_db.data_elements.bpk_enum import Bpk
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem


@dataclass(unsafe_hash=True)
class Node:
    """A single node."""

    id: str
    ecos_id: str
    switch_item: SwitchItem
    ts_number: str
    bpk: Bpk
    coords: np.ndarray
