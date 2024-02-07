"""Command pattern Pandas."""
from __future__ import annotations

import pandas as pd

from ebl_coords.backend.command.base import Command
from ebl_coords.decorators import override


class UpdateStateCommand(Command):
    """Update value in state column.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: dict[str, int | str], context: pd.DataFrame) -> None:
        """Initialize with ecos Dataframe.

        Args:
            content (Dict[str, int | str]): keys = id, ip, state.
            context (pd.DataFrame): ecos Dataframe.
        """
        super().__init__(content, context)
        self.content: dict[str, int | str]
        self.context: pd.DataFrame

    @override
    def run(self) -> None:
        """Update existing state entry."""
        ecos_id = self.content["id"]
        ip = self.content["ip"]
        state = self.content["state"]

        index = self.context.loc[
            (self.context.id == ecos_id) & (self.context.ip == ip)
        ].index
        self.context.loc[index, "state"] = state
