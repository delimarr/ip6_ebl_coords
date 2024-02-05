"""Command pattern Graph Db."""
from __future__ import annotations

from ebl_coords.backend.command.base import Command
from ebl_coords.decorators import override
from ebl_coords.graph_db.graph_db_api import GraphDbApi


class DbCommand(Command):
    """Command pattern.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: str) -> None:
        """Initialize command with query.

        Args:
            content (str): query call
        """
        super().__init__(content)
        self.context: GraphDbApi = GraphDbApi()

    @override
    def run(self) -> None:
        """Execute query."""
        self.context.run_query(self.content)
