"""Neo4j edge."""
from dataclasses import dataclass

from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.node_dc import Node


@dataclass(unsafe_hash=True)
class Edge:
    """A single directional edge."""

    source: Node
    dest: Node
    relation: EdgeRelation
    distance: float
