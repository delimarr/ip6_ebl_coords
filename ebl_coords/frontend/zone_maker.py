"""Draws Zones."""
from typing import List

from PyQt6 import QtGui
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QLabel

GREEN = QColor("#9ACC99")
GREY = QColor("#8F8F8F")


class ZoneMaker:
    """Provides functionality to draw zones."""

    def __init__(self, zone_map: QLabel):
        """Init values."""
        self.width: int = 0
        self.height: int = 0
        self.block_size: int = 41
        self.map: QLabel = zone_map

    def _clear(self) -> None:
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

    def draw_grid(self, width: int, height: int) -> dict[str, List[str]]:
        """Draws a grid.

        Args:
            width (int): width in blocks
            height (int): height in blocks

        Returns:
            dict: {"keys_width": keys_width, "keys_height": keys_height} containing the width and height coordinates
        """
        self.width = width
        self.height = height
        width = self.width + 1
        height = self.height + 1
        block_size = self.block_size
        width_pixels = width * block_size + 1
        height_pixels = height * block_size + 1
        self.map.setFixedSize(width_pixels, height_pixels)
        self.map.setPixmap(QtGui.QPixmap(self.map.size()))
        self._clear()

        keys_width = []
        keys_height = []

        for i in range(1, width):
            x_i = i * block_size
            self._draw_text(str(i - 1), x_i, block_size * 3 // 4)
            keys_width.append(str(i - 1))

        for i in range(1, width + 1):
            x_i = i * block_size
            self._draw_line(x_i, block_size, x_i, height * block_size)

        for i in range(1, height):
            y_i = i * block_size
            self._draw_text(str(i - 1), block_size // 4, y_i + block_size * 3 // 4)
            keys_height.append(str(i - 1))

        for i in range(1, height + 1):
            y_i = i * block_size
            self._draw_line(block_size, y_i, width * block_size, y_i)

        return {"keys_width": keys_width, "keys_height": keys_height}

    def draw_grid_line(self, u1: int, v1: int, u2: int, v2: int) -> None:
        """Draws a line from point 1 to 2 in grid system.

        Args:
            u1 (int): Point 1 u-coordinate
            v1 (int): Point 1 v-coordinate
            u2 (int): Point 2 u-coordinate
            v2 (int): Point 2 v-coordinate
        """
        self._draw_line(
            (u1 + 1) * self.block_size + self.block_size // 2,
            (v1 + 1) * self.block_size + self.block_size // 2,
            (u2 + 1) * self.block_size + self.block_size // 2,
            (v2 + 1) * self.block_size + self.block_size // 2,
        )
