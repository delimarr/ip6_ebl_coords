"""Notify user when trainswitch is calibrated."""
from ebl_coords.backend.abstract.observer import Observer
from ebl_coords.frontend.main_gui import Ui_MainWindow


class TsMeasureObserver(Observer):
    """Get notified if trainswitch is calibrated.

    Args:
        Observer (_type_): observer interface
    """

    def __init__(self, ui: Ui_MainWindow) -> None:
        """Initialize with ui.

        Args:
            ui (Ui_MainWindow): ui of mainwindow.
        """
        self.ui = ui

    def popup(self) -> None:
        """Show start calibration message."""
        self.ui.statusbar.showMessage("Bitte warten, Weiche wird eingemessen.")

    def update(self) -> None:
        """Show finished calibration message."""
        x, y, z = self.result
        self.ui.statusbar.showMessage(f"Weiche bei: ({x}, {y}, {z}) eingemessen.")
