"""Start the EBL-GUI application."""
from __future__ import annotations

import sys
import warnings
from queue import Queue
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow

from ebl_coords.backend.constants import CALLBACK_DT, CONFIG_JSON
from ebl_coords.backend.ecos import load_config
from ebl_coords.backend.observable.ecos_subject import EcosSubject
from ebl_coords.backend.observable.gtcommand_subject import GtCommandSubject
from ebl_coords.frontend.main_gui import Ui_MainWindow
from ebl_coords.frontend.map_editor import MapEditor
from ebl_coords.frontend.strecken_editor import StreckenEditor
from ebl_coords.frontend.weichen_editor import WeichenEditor
from ebl_coords.graph_db.graph_db_api import GraphDbApi

if TYPE_CHECKING:
    from ebl_coords.backend.command.base import Command


class MainWindow(QMainWindow):  # type: ignore
    """A Pyqt6 Mainwindow."""

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

        self.bpks, self.ecos_config = load_config(CONFIG_JSON)
        self.ecos_df: pd.DataFrame
        self.set_ecos_df()

        self.gtcommand = GtCommandSubject()
        self.ecos = EcosSubject(self.ecos_config, self.ecos_df["id"])
        # self.ecos.start_record()

        self.map_editor = MapEditor(self)
        self.map_editor.register_observers()
        self.strecken_editor = StreckenEditor(self)
        self.weichen_editor = WeichenEditor(self)

        self.show()

    def set_ecos_df(self) -> None:
        """Build and set ecos Dataframe containing the state of all train switches."""
        self.ecos_df = pd.read_csv("./tmp/ecos.csv")
        self.ecos_df = self.ecos_df.loc[self.ecos_df.protocol == "DCC"]
        self.ecos_df = self.ecos_df.loc[self.ecos_df.name1.isin(list(self.bpks))]
        warnings.warn("used ecos mock")
        cmd = "MATCH (n) RETURN n.node_id AS node_id, n.ecos_id AS dcc, n.bhf AS bpk"
        df = self.ecos_df
        db = GraphDbApi().run_query(cmd)[::2]
        db.bpk = '"' + db.bpk + '"'
        df.insert(df.shape[1], column="guid", value=np.nan)
        for _, row in db.iterrows():
            df.guid.loc[
                (df["name1"] == row.bpk) & (df["addr"] == int(row.dcc))
            ] = row.node_id

        df.insert(df.shape[1], column="ip", value=np.nan)
        k = -1
        ips = list(self.ecos_config["bpk_ip"].values())[1:]
        for i, row in df.iterrows():
            if row.id == 20_000:
                k += 1
            df.loc[i, "ip"] = ips[k]

        self.ecos_df = df.dropna()

    def my_callback(self) -> None:
        """Execute this function every DELTA_DT ms."""
        while not self.command_queue.empty():
            cmd = self.command_queue.get()
            cmd.run()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())
