"""Command pattern Pandas."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from ebl_coords.backend.command.command import Command
from ebl_coords.backend.constants import ECOS_DF_LOCK
from ebl_coords.decorators import override

if TYPE_CHECKING:
    from ebl_coords.main import EblCoords


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

        with ECOS_DF_LOCK:
            index = self.context.loc[(self.context.id == ecos_id) & (self.context.ip == ip)].index
            self.context.loc[index, "state"] = state


class UpdateEocsDfCommand(Command):
    """Update the EcosDataframe from sockets.

    Args:
        Command (_type_): interface
    """

    def __init__(self, context: EblCoords) -> None:
        """Initialize this command.

        Args:
            context (EblCoords): ebl_coords
        """
        super().__init__(None, context)
        self.context: EblCoords

    @override
    def run(self) -> None:
        """Update and set ecos_df in ebl_coords."""
        self.context.update_ecos_df()
