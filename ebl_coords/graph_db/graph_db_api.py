"""Module to interact with neo4j."""
from os import environ
from typing import List, Tuple

import pandas as pd
from neo4j import GraphDatabase

from ebl_coords.backend.constants import NEO4J_PASSWD, NEO4J_URI_CONTAINER
from ebl_coords.backend.constants import NEO4J_URI_LOCAL, NEO4J_USR
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.query_generator import drop_db


class _InnerApi:
    """Class to interact with neo4j."""

    def __init__(self) -> None:
        """Initialize the API."""
        neo4j_uri: str
        if "DEV_CONTAINER" in environ:
            neo4j_uri = NEO4J_URI_CONTAINER
        else:
            neo4j_uri = NEO4J_URI_LOCAL
        self.session = GraphDatabase.driver(
            neo4j_uri, auth=(NEO4J_USR, NEO4J_PASSWD)
        ).session()

    def __del__(self) -> None:
        """Closes the session."""
        self.session.close()

    def run_query(self, query: str) -> pd.DataFrame:
        """Run query on graph database.

        Args:
            query (str): query to execute

        Returns:
            pd.DataFrame: resulting data as a dataframe. Can be empty.
        """
        return self.session.run(query).to_df()

    # for delete make console interactive and ask if user is a dumbass
    def drop_db(self) -> None:
        """Deletes all data on DB."""
        self.session.run(drop_db())

    def edges_tostring(self) -> List[Tuple[str, str]]:
        r"""Return all non-doublevertex edges in db as string.

        Returns:
            List[Tuple[str, str]]: list of: (guid edge, edge string: bpk1_number1\trelation\tbpk2_number2)
        """
        edges = []
        for relation in EdgeRelation:
            if relation == EdgeRelation.DOUBLE_VERTEX:
                continue
            cmd = f"MATCH (n1)-[r:{relation.name}]->(n2) RETURN n1.bhf, n1.name, n1.node_id, n2.bhf, n2.name, r.edge_id"
            df = self.run_query(cmd)
            df.sort_values(by=["n1.bhf", "n1.name"], inplace=True)
            if df.size > 0:
                for _, row in df.iterrows():
                    edge = f"{row['n1.bhf']}_{row['n1.name']}\t{relation.value}\t{row['n2.bhf']}_{row['n2.name']}"
                    edges.append((row["r.edge_id"], edge))
        return edges


class GraphDbApi(_InnerApi):
    """Singleton wrapper class for Api."""

    _api = None

    def __new__(cls) -> _InnerApi:  # type: ignore
        """Return singleton or create if it does not exist yet."""
        if cls._api is None:
            cls._api = super(_InnerApi, cls).__new__(cls)
        return cls._api
