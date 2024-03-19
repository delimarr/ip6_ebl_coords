"""Main Gui."""
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow

from ebl_coords.backend.constants import CALLBACK_DT_MS
from ebl_coords.frontend.main_gui import Ui_MainWindow
from ebl_coords.frontend.map_editor import MapEditor
from ebl_coords.frontend.strecken_editor import StreckenEditor
from ebl_coords.frontend.weichen_editor import WeichenEditor

if TYPE_CHECKING:
    from ebl_coords.main import EblCoords


class Gui(QMainWindow):  # type: ignore
    """The Gui class."""

    def __init__(self, ebl_coords: EblCoords) -> None:
        """Create a Gui for EblCoords backend."""
        self.app = QApplication(sys.argv)
        super().__init__()

        self.gui_queue = ebl_coords.gui_queue
        self.worker_queue = ebl_coords.worker_queue
        self.ecos_df = ebl_coords.ecos_df
        self.ebl_coords = ebl_coords

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # type: ignore

        self.map_editor = MapEditor(self)
        self.strecken_editor = StreckenEditor(self)
        self.weichen_editor = WeichenEditor(self)

        self.map_editor.register_observers()

        self.callback_timer: QTimer

        self.show()

    def _register_invoker(self) -> None:
        """Register invoker."""
        self.callback_timer = QTimer()
        self.callback_timer.timeout.connect(self._invoke)
        self.callback_timer.start(CALLBACK_DT_MS)

    def _invoke(self) -> None:
        """Execute this function every DELTA_DT ms."""
        while not self.gui_queue.empty():
            cmd = self.gui_queue.get()
            cmd.run()

    def run(self) -> None:
        """Start invoker and set exit app."""
        self._register_invoker()
        sys.exit(self.app.exec())
