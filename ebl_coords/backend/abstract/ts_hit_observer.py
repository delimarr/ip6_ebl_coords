"""Train travels over trainswitch."""
from PyQt6.QtCore import pyqtSignal

from ebl_coords.backend.abstract.observer import Observer


class TsHitObserver(Observer):
    """Emit signal if a train is detected on a trainswitch.

    Args:
        Observer (_type_): observer interface
    """

    def __init__(self) -> None:
        """Initialize pyqtsignal."""
        self.redraw_zone_signal = pyqtSignal()

    def update(self) -> None:
        """Emit redraw signal."""
        self.redraw_zone_signal.emit()
