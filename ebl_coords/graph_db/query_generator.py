"""Get query to generate double nodes and eges in neo4j."""
from __future__ import annotations

from uuid import uuid4

from ebl_coords.graph_db.data_elements.edge_dc import Edge
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.node_dc import Node
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem


def generate_guid() -> str:
    """Generate a random guid."""
    return "guid_" + str(uuid4()).partition("-")[0]


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
                name: '{node.ts_number}', \
                ecos_id: '{node.ecos_id}', \
                bhf: '{node.bpk.name}', \
                x: {node.coords[0]}, \
                y: {node.coords[1]}, \
                z: {node.coords[2]} \
            }}\
        )
    """.replace(
        " ", ""
    )


def double_node(template_node: Node) -> tuple[str, tuple[Node, Node]]:
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
    edge = Edge(
        id=generate_guid(),
        source=node1,
        dest=node2,
        relation=EdgeRelation.DOUBLE_VERTEX,
        distance=0,
    )

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
        MATCH(source:{edge.source.switch_item.name}{{node_id: '{edge.source.id}'}})\
        MATCH(dest:{edge.dest.switch_item.name}{{node_id: '{edge.dest.id}'}})\
        CREATE(source)-[:{edge.relation.name}{{distance: {edge.distance}, target: '{edge.target.name}', edge_id: '{edge.id}'}}]->(dest);\
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
    edge_id = template_edge.id
    source = template_edge.source
    dest = template_edge.dest
    distance = template_edge.distance
    relation = template_edge.relation.name

    cmd = f"""\
        MATCH(source:{source.switch_item.name}{{node_id: '{source.id}'}})
        MATCH(dest:{dest.switch_item.name}{{node_id: '{dest.id}'}})
        CREATE(source)-[:{relation}{{distance: {distance}, target: '{relation}', edge_id: '{edge_id}_0'}}]->(dest)
        CREATE(dest)-[:{relation}{{distance: {distance}, target: '{relation}', edge_id: '{edge_id}_1'}}]->(source)
    """.replace(
        " ", ""
    )
    return cmd


def get_double_nodes(guid: str) -> str:
    """Create query to get both nodes in a double vertex.

    Args:
        guid (str): node_id of one of the nodes.

    Returns:
        str: query call
    """
    double_vertex = EdgeRelation.DOUBLE_VERTEX.name
    weiche = SwitchItem.WEICHE.name
    vals = "n1.name, n1.bhf, n1.ecos_id, n1.x, n1.y, n1.z"
    return f"""
    MATCH(n1:{weiche}{{node_id:'{guid}'}})-[:{double_vertex}]->(n2:{weiche}) RETURN {vals};
    """


def update_double_nodes(node: Node) -> str:
    """Update a double node.

    Args:
        node (Node): new node values, with one existing id.

    Returns:
        str: query call
    """
    double_vertex = EdgeRelation.DOUBLE_VERTEX.name
    weiche = SwitchItem.WEICHE.name
    return f"""
    MATCH(n1:{weiche}{{node_id:'{node.id}'}})-[:{double_vertex}]->(n2:{weiche})\
    SET n1.bhf = '{node.bpk.name}'\
    SET n2.bhf = '{node.bpk.name}'\
    SET n1.name = '{node.ts_number}'\
    SET n2.name = '{node.ts_number}'\
    SET n1.ecos_id = '{node.ecos_id}'\
    SET n2.ecos_id = '{node.ecos_id}';
    """


def drop_db() -> str:
    """Get query delete all.

    Returns:
        str: query call
    """
    return "MATCH (n) \n DETACH DELETE n; \n"
