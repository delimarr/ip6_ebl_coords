"""Neo4j Dachsburg-Ring example."""
import json
from typing import Dict, List, Tuple
from uuid import uuid4

import numpy as np

from ebl_coords.graph_db.api import Api
from ebl_coords.graph_db.data_elements.bahnhof_enum import Bhf
from ebl_coords.graph_db.data_elements.edge_dc import Edge
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.node_dc import Node
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem
from ebl_coords.graph_db.query_generator import bidirectional_edge, double_node


def guid() -> str:
    """Get a random guid."""
    return "guid_" + str(uuid4()).partition("-")[0]


graph_db = Api()
graph_db.drop_db()

WEICHEN_FILE = "./data/weichen_run_7_9.json"


w_tps: List[Node] = []
double_nodes: Dict[str, Tuple[Node, Node]] = {"DAB": {}, "ENS": {}, "CHA": {}}
query: List[str] = []

with open(WEICHEN_FILE, encoding="utf-8") as fd:
    weichen_config = json.load(fd)

for bhf, weichen in weichen_config.items():
    for weiche in weichen:
        dcc = weichen_config[bhf][weiche]["dcc"]
        coords = weichen_config[bhf][weiche]["coords"]
        node = Node(
            id=guid(),
            ecos_id=dcc,
            switch_item=SwitchItem.WEICHE,
            name=weiche,
            bhf=Bhf[bhf],
            coords=np.array(coords, dtype=np.float32),
        )
        w_tps.append(node)

for w_tp in w_tps:
    cmd, nodes = double_node(w_tp)
    double_nodes[w_tp.bhf.name][w_tp.name] = nodes
    graph_db.run_query(cmd)

rails_dab = [
    Edge(
        source=double_nodes["DAB"]["ew01"][1],
        dest=double_nodes["DAB"]["ew02"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew01"][1],
        dest=double_nodes["DAB"]["ew04"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew02"][1],
        dest=double_nodes["DAB"]["ew03"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew03"][1],
        dest=double_nodes["DAB"]["ew04"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew03"][1],
        dest=double_nodes["DAB"]["ew06"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew04"][1],
        dest=double_nodes["DAB"]["ew05"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew05"][1],
        dest=double_nodes["DAB"]["ew10"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew05"][1],
        dest=double_nodes["DAB"]["ew10"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=2,
    ),
    Edge(
        source=double_nodes["DAB"]["ew06"][1],
        dest=double_nodes["DAB"]["ew07"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew06"][1],
        dest=double_nodes["DAB"]["ew09"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew07"][1],
        dest=double_nodes["DAB"]["ew08"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew08"][1],
        dest=double_nodes["DAB"]["ew09"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew09"][1],
        dest=double_nodes["DAB"]["ew11"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew10"][1],
        dest=double_nodes["DAB"]["ew12"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew11"][1],
        dest=double_nodes["DAB"]["ew12"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew11"][1],
        dest=double_nodes["DAB"]["ew14"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew12"][1],
        dest=double_nodes["DAB"]["ew13"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew13"][1],
        dest=double_nodes["DAB"]["ew14"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
]

rails_ens_cha = [
    Edge(
        source=double_nodes["CHA"]["ew01"][1],
        dest=double_nodes["CHA"]["ew02"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["CHA"]["ew01"][1],
        dest=double_nodes["CHA"]["ew04"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["CHA"]["ew01"][0],
        dest=double_nodes["CHA"]["ew07"][1],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["CHA"]["ew02"][1],
        dest=double_nodes["CHA"]["ew03"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["CHA"]["ew02"][0],
        dest=double_nodes["CHA"]["ew08"][1],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["CHA"]["ew03"][1],
        dest=double_nodes["CHA"]["ew04"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["CHA"]["ew05"][1],
        dest=double_nodes["CHA"]["ew07"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["CHA"]["ew05"][1],
        dest=double_nodes["ENS"]["w1"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["CHA"]["ew06"][1],
        dest=double_nodes["CHA"]["ew08"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["CHA"]["ew06"][1],
        dest=double_nodes["ENS"]["w2"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["ENS"]["w1"][1],
        dest=double_nodes["ENS"]["w2"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
]

rails_connect = [
    Edge(
        source=double_nodes["DAB"]["ew01"][0],
        dest=double_nodes["CHA"]["ew03"][1],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew02"][0],
        dest=double_nodes["CHA"]["ew04"][1],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew13"][1],
        dest=double_nodes["CHA"]["ew06"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
    Edge(
        source=double_nodes["DAB"]["ew14"][1],
        dest=double_nodes["CHA"]["ew05"][0],
        relation=EdgeRelation.TRAIN_RAIL,
        distance=1,
    ),
]

for rail in rails_dab:
    cmd = bidirectional_edge(rail)
    graph_db.run_query(cmd)

for rail in rails_ens_cha:
    cmd = bidirectional_edge(rail)
    graph_db.run_query(cmd)

for rail in rails_connect:
    cmd = bidirectional_edge(rail)
    graph_db.run_query(cmd)
