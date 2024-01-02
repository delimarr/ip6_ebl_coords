"""Start the EBL-GUI application."""
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from ebl_coords.frontend.main_gui import Ui_MainWindow


class MainWindow(QMainWindow):  # type: ignore
    """A Pyqt6 Mainwindow."""

    def __init__(self) -> None:
        """Initialize and show the gui."""
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # type: ignore
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())
