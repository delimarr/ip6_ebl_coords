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
    return f"""\
        CREATE(\
        {node.id}:{node.switch_item.name} \
            {{\
                node_id: '{node.id}', \
                name: '{node.name}', \
                ecos_id: '{node.ecos_id}', \
                bhf: '{node.bhf.name}', \
                x: {node.coords[0]}, \
                y: {node.coords[1]}, \
                z: {node.coords[2]} \
            }}\
        )
    """.replace(
        " ", ""
    )


def double_node(template_node: Node) -> Tuple[str, Tuple[Node, Node]]:
    """Create query for bidirectional double node.

    Args:
        template_node (Node): template for both nodes.

    Returns:
        str: query call, new nodes
    """
    node1 = Node(**template_node.__dict__)
    node1.id = node1.id + "_0"
    node2 = Node(**template_node.__dict__)
    node2.id = node2.id + "_1"
    edge = Edge(node1, node2, EdgeRelation.DOUBLE_VERTEX, distance=0)

    node1_cmd = single_node(node1)
    node2_cmd = single_node(node2)
    edge_cmd = bidirectional_edge(edge)

    with_statement = f"WITH {node1.id}, {node2.id}\n"

    cmd = node1_cmd + node2_cmd + with_statement + edge_cmd

    return cmd, (node1, node2)


def single_edge(edge: Edge) -> str:
    """Create query for directional edge.

    Args:
        edge (Edge): edge

    Returns:
        str: query call
    """
    cmd = f"""\
        MATCH(source:{edge.source.switch_item.name}{{node_id: '{edge.source.id}'}})
        MATCH(dest:{edge.dest.switch_item.name}{{node_id: '{edge.dest.id}'}})
        CREATE(source)-[:{edge.relation}{{distance: {edge.distance}}}]->(dest)
    """.replace(
        " ", ""
    )
    return cmd


def bidirectional_edge(template_edge: Edge) -> str:
    """Create query for bidirectional edge.

    Args:
        template_edge (Edge): template for both edges.

    Returns:
        str : query call
    """
    source = template_edge.source
    dest = template_edge.dest
    distance = template_edge.distance
    relation = template_edge.relation.name

    cmd = f"""\
        MATCH(source:{source.switch_item.name}{{node_id: '{source.id}'}})
        MATCH(dest:{dest.switch_item.name}{{node_id: '{dest.id}'}})
        CREATE(source)-[:{relation}{{distance: {distance}}}]->(dest)
        CREATE(dest)-[:{relation}{{distance: {distance}}}]->(source)
    """.replace(
        " ", ""
    )
    return cmd


def drop_db() -> str:
    """Get query delete all.

    Returns:
        str: query call
    """
    return "MATCH (n) \n DETACH DELETE n; \n"
