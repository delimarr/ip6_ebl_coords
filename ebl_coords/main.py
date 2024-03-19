"""Start the EBL application."""
from __future__ import annotations

from queue import Queue
from typing import TYPE_CHECKING

import pandas as pd

from ebl_coords.backend.command.invoker import Invoker
from ebl_coords.backend.constants import CALLBACK_DT_MS, CONFIG_JSON, ECOS_DF_LOCK
from ebl_coords.backend.ecos import get_ecos_df, load_config
from ebl_coords.backend.observable.ecos_subject import EcosSubject
from ebl_coords.frontend.gui import Gui
from ebl_coords.graph_db.graph_db_api import GraphDbApi

if TYPE_CHECKING:
    from ebl_coords.backend.command.command import Command


class EblCoords:
    """Main Backend."""

    def __init__(self) -> None:
        """Initialize and show the gui."""
        super().__init__()

        self.worker_queue: Queue[Command] = Queue()
        self.invoker = Invoker()
        self.invoker.start_loop(self.worker_queue, CALLBACK_DT_MS / 1000)

        self.bpks, self.ecos_config = load_config(config_file=CONFIG_JSON)
        self.ecos_df: pd.DataFrame
        self.update_ecos_df()

        self.ecos = EcosSubject(ecos_config=self.ecos_config, ecos_ids=self.ecos_df["id"])
        self.ecos.start_record()

        self.graphdb = GraphDbApi()

        self.gui_queue: Queue[Command] = Queue()
        self.gui = Gui(ebl_coords=self)
        self.gui.run()

    def update_ecos_df(self) -> None:
        """Crawl all ecos sockets, rebuild ecos_df."""
        df = get_ecos_df(config=self.ecos_config, bpks=self.bpks)
        with ECOS_DF_LOCK:
            self.ecos_df = df


if __name__ == "__main__":
    ebl_coords = EblCoords()
