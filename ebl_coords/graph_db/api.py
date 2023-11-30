"""Module to interact with neo4j."""
from neo4j import GraphDatabase

from ebl_coords.backend.constants import NEO4J_PASSWD, NEO4J_URI_LOCAL, NEO4J_USR
from ebl_coords.graph_db.query_generator import drop_db


class Api:
    """Class to interact with neo4j."""

    def __init__(self) -> None:
        """Initialize the API."""
        self.session = GraphDatabase.driver(
            NEO4J_URI_LOCAL, auth=(NEO4J_USR, NEO4J_PASSWD)
        ).session()

    def run_query(self, query: str) -> None:
        """Run a query on the database.

        Args:
            query (str): Database query
        """
        self.session.run(query)

    # for delete make console interactive and ask if user is a dumbass
    def drop_db(self) -> None:
        """Deletes all data on DB."""
        self.session.run(drop_db())
