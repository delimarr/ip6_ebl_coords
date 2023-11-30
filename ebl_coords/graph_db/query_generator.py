"""Get query to generate double nodes and eges in neo4j."""
from typing import Tuple

from ebl_coords.graph_db.data_elements.edge_dc import Edge
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.node_dc import Node


def single_node(node: Node) -> str:
    """Create query for single node.

    Args:
        node (Node): node

    Returns:
        str: query call
    """
    return f"""
        (\
        {node.id}:{node.switch_item.name} \
            {{\
                name: '{node.name}', \
                ecos_id: '{node.ecos_id}', \
                bhf: '{node.bhf.name}', \
                x: {node.coords[0]}, \
                y: {node.coords[1]}, \
                z: {node.coords[2]} \
            }}\
        ),
    """


def directional_edge(edge: Edge) -> str:
    """Create a query for a single directional edge.

    Args:
        edge (Edge): edge

    Returns:
        str: query call
    """
    return f"""
        (\
        {edge.source.id})\
            -[:{edge.relation.name} {{distance:{edge.distance}}}]->\
        ({edge.dest.id}\
        ),
    """


def double_node(template_node: Node) -> Tuple[str, Tuple[Node, Node]]:
    """Create query for bidirectional double node.

    Args:
        template_node (Node): template for both nodes.

    Returns:
        str: query call, new nodes
    """
    node1 = Node(**template_node.__dict__)
    node1.id = node1.id + "_1"
    node2 = Node(**template_node.__dict__)
    node2.id = node2.id + "_2"

    res = single_node(node1)
    res += single_node(node2)

    edge_12 = Edge(node1, node2, EdgeRelation.DOUBLE_VERTEX, distance=0)
    edge_21 = Edge(node2, node1, EdgeRelation.DOUBLE_VERTEX, distance=0)
    res += directional_edge(edge_12)
    res += directional_edge(edge_21)
    return res, (node1, node2)


def bidirectional_edge(template_edge: Edge) -> Tuple[str, Tuple[Edge, Edge]]:
    """Create query for bidirectional edge.

    Args:
        template_edge (Edge): template for both edges.

    Returns:
        Tuple[str, Tuple[Edge, Edge]]: query call, new edges
    """
    edge1 = Edge(**template_edge.__dict__)
    edge2 = Edge(**template_edge.__dict__)
    edge2.source = edge1.dest
    edge2.dest = edge1.source

    res = directional_edge(edge1)
    res += directional_edge(edge2)

    return res, (edge1, edge2)


def drop_db() -> str:
    """Get query delete all.

    Returns:
        str: query call
    """
    return "MATCH (n) \n DETACH DELETE n; \n"
