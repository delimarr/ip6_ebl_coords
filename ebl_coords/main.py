"""Start the EBL-GUI application."""
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from ebl_coords.backend.abstract.gtcommand_subject import GtCommandSubject
from ebl_coords.frontend.main_gui import Ui_MainWindow
from ebl_coords.frontend.map_editor import MapEditor
from ebl_coords.frontend.strecken_editor import StreckenEditor
from ebl_coords.frontend.weichen_editor import WeichenEditor
from ebl_coords.graph_db.api import Api


class MainWindow(QMainWindow):  # type: ignore
    """A Pyqt6 Mainwindow."""

    def __init__(self) -> None:
        """Initialize and show the gui."""
        super().__init__()

        self.graph_db = Api()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # type: ignore

        self.gtcommand_subject = GtCommandSubject("127.0.0.1", 42042, self.graph_db)

        self.strecken_editor = StreckenEditor(self.ui, self.graph_db)
        self.weichen_editor = WeichenEditor(
            ui=self.ui,
            graph_db=self.graph_db,
            strecken_editor=self.strecken_editor,
            gtcommand_subject=self.gtcommand_subject,
        )
        self.map_editor = MapEditor(self.ui, self.graph_db, self.gtcommand_subject)

        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())
