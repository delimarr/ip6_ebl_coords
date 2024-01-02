"""All edge relations in the DB."""
from enum import Enum


class EdgeRelation(Enum):
    """Enum edge relation."""

    DOUBLE_VERTEX = "DOUBLE_VERTEX"
    TRAIN_RAIL = "TRAIN_RAIL"
