"""All edge relations in the DB."""
from enum import Enum


class EdgeRelation(Enum):
    """Enum edge relation."""

    DOUBLE_VERTEX = "DOUBLE_VERTEX"
    NEUTRAL = "Anfang"
    DEFLECTION = "Ablenkung"
    STRAIGHT = "Gerade"


EDGE_RELATION_TO_ENUM = {member.value: member for member in EdgeRelation}

TRAINRAILS = [
    EdgeRelation.NEUTRAL.value,
    EdgeRelation.DEFLECTION.value,
    EdgeRelation.STRAIGHT.value,
]
