"""Start the EBL-GUI application."""
from __future__ import annotations

import sys
from queue import Queue
from typing import TYPE_CHECKING

import pandas as pd
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow

from ebl_coords.backend.constants import CALLBACK_DT
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

        self.ts_df: pd.DataFrame

        self.gtcommand = GtCommandSubject()

        self.strecken_editor = StreckenEditor(self)
        self.weichen_editor = WeichenEditor(self)
        self.map_editor = MapEditor(self)

        self.show()

    def my_callback(self) -> None:
        """Execute this function every DELTA_DT ms."""
        while not self.command_queue.empty():
            cmd = self.command_queue.get()
            cmd.run()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())
