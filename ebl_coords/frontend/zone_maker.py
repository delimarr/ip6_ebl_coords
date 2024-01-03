"""Draws Zones."""
from typing import Tuple

from PyQt6 import QtGui
from PyQt6.QtGui import QColor, QPen

from ebl_coords.frontend.custom_widgets import ClickableLabel

GREEN = QColor("#9ACC99")
GREY = QColor("#8F8F8F")


class ZoneMaker:
    """Provides functionality to draw zones."""

    def __init__(self, zone_map: ClickableLabel, block_size: int = 41):
        """Init values."""
        self.width: int = 0
        self.height: int = 0
        self.block_size: int = block_size
        self.map = zone_map

    def clear(self) -> None:
        """Clears the map label."""
        canvas = self.map.pixmap()
        canvas.fill(GREEN)
        self.map.setPixmap(canvas)

    def _draw_line(self, u1: int, v1: int, u2: int, v2: int) -> None:
        """Draws a line from point 1 to point 2 on the grid system.

        Args:
            u1 (int): Point 1 u-coordinate
            v1 (int): Point 1 v-coordinate
            u2 (int): Point 2 u-coordinate
            v2 (int): Point 2 v-coordinate
        """
        canvas = self.map.pixmap()
        painter = QtGui.QPainter(canvas)
        painter.setPen(GREY)
        painter.drawLine(u1, v1, u2, v2)
        painter.end()
        self.map.setPixmap(canvas)

    def _draw_text(self, text: str, u: int, v: int) -> None:
        """Write text at coordinates in grid system.

        Args:
            text (str): Text
            u (int): u-coordinate
            v (int): v-coordinate
        """
        canvas = self.map.pixmap()
        painter = QtGui.QPainter(canvas)
        painter.drawText(u, v, text)
        painter.end()
        self.map.setPixmap(canvas)

    def draw_grid(self, width: int, height: int) -> None:
        """Draws a grid.

        Args:
            width (int): width in blocks
            height (int): height in blocks
        """
        self.width = width
        self.height = height
        block_size = self.block_size
        width_pixels = width * block_size + 1
        height_pixels = height * block_size + 1
        self.map.setFixedSize(width_pixels, height_pixels)
        self.map.setPixmap(QtGui.QPixmap(self.map.size()))
        self.clear()

        # vertical lines
        for i in range(0, width + 1):
            x_i = i * block_size
            self._draw_line(x_i, 0, x_i, height * block_size)

        # horizontal lines
        for i in range(0, height + 1):
            y_i = i * block_size
            self._draw_line(0, y_i, width * block_size, y_i)

    def draw_grid_line(self, u1: int, v1: int, u2: int, v2: int) -> None:
        """Draws a line from point 1 to 2 in grid system.

        Args:
            u1 (int): Point 1 u-coordinate
            v1 (int): Point 1 v-coordinate
            u2 (int): Point 2 u-coordinate
            v2 (int): Point 2 v-coordinate
        """
        self._draw_line(
            u1 * self.block_size + self.block_size // 2,
            v1 * self.block_size + self.block_size // 2,
            u2 * self.block_size + self.block_size // 2,
            v2 * self.block_size + self.block_size // 2,
        )

    def draw_grid_point(self, u: int, v: int) -> None:
        """Draw a point in the grid.

        Args:
            u (int): grid tile number in x axis, starting with 0
            v (int): grid tile number in y axis, starting with 0
        """
        canvas = self.map.pixmap()
        painter = QtGui.QPainter(canvas)
        pen = QPen(GREY)
        pen.setWidth(self.block_size // 3)
        painter.setPen(pen)
        u = u * self.block_size + self.block_size // 2
        v = v * self.block_size + self.block_size // 2
        painter.drawPoint(u, v)
        painter.end()
        self.map.setPixmap(canvas)

    def get_grid_coords(self, x: int, y: int) -> Tuple[int, int]:
        """Get grid tile coordinates from pixels.

        Args:
            x (int): pixel x value
            y (int): pixel y value

        Returns:
            Tuple[int, int]: grid tile coordinates, top left is (0, 0)
        """
        u = x // self.block_size
        v = y // self.block_size
        return (u, v)
