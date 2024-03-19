"""Start the EBL application."""
from __future__ import annotations

from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING

import pandas as pd

from ebl_coords.backend.constants import CONFIG_JSON, ECOS_DF_LOCK
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
        self.callback_timer = QTimer()
        self.callback_timer.timeout.connect(self.my_callback)
        self.callback_timer.start(CALLBACK_DT)

        self.graph_db = GraphDbApi()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # type: ignore

        self.command_queue: Queue[Command] = Queue()

        self.bpks, self.ecos_config = load_config(config_file=CONFIG_JSON)
        self.ecos_df: pd.DataFrame
        self.update_ecos_df()

        self.ecos = EcosSubject(ecos_config=self.ecos_config, ecos_ids=self.ecos_df["id"])
        self.ecos.start_record()

        self.graphdb = GraphDbApi()

        self.gui_queue: Queue[Command] = Queue()
        self.gui = Gui(ebl_coords=self)
        self.gui_tread = Thread(target=self.gui.run)
        self.gui_tread.start()

    def keep_alive(self) -> None:
        """Wait for gui thread termination."""
        self.gui_tread.join()

    def update_ecos_df(self) -> None:
        """Crawl all ecos, rebuild ecos_df."""
        df = get_ecos_df(config=self.ecos_config, bpks=self.bpks)
        with ECOS_DF_LOCK:
            self.ecos_df = df


if __name__ == "__main__":
    ebl_coords = EblCoords()
    ebl_coords.keep_alive()
