"""Module to interact with neo4j."""
from os import environ

import pandas as pd
from neo4j import GraphDatabase

from ebl_coords.backend.constants import NEO4J_PASSWD, NEO4J_URI_CONTAINER
from ebl_coords.backend.constants import NEO4J_URI_LOCAL, NEO4J_USR
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

    def run_query(self, query: str) -> pd.DataFrame:
        """Run query on graph database.

        Args:
            query (str): query to execute

        Returns:
            pd.DataFrame: resulting data as a dataframe. Can be empty.
        """
        return self.session.run(query).to_df(expand=False)

    # for delete make console interactive and ask if user is a dumbass
    def drop_db(self) -> None:
        """Deletes all data on DB."""
        self.session.run(drop_db())

    def __del__(self) -> None:
        """Closes the session."""
        self.session.close()


class Api(_InnerApi):
    """Singleton wrapper class for Api."""

    _api = None

    def __new__(cls) -> _InnerApi:  # type: ignore
        """Return singleton or create if it does not exist yet."""
        if cls._api is None:
            cls._api = super(_InnerApi, cls).__new__(cls)
        return cls._api
