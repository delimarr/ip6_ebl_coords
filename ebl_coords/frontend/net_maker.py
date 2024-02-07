"""Draws Zones."""
from typing import Tuple

from PyQt6 import QtGui
from PyQt6.QtGui import QColor, QPen

from ebl_coords.backend.constants import BACKGROUND_HEX, BLOCK_SIZE, GRID_HEX, LINE_HEX
from ebl_coords.backend.constants import POINT_HEX, TEXT_HEX
from ebl_coords.frontend.custom_widgets import ClickableLabel


class NetMaker:
    """Provides functionality to draw nets."""

    def __init__(self, zone_map: ClickableLabel, block_size: int = BLOCK_SIZE):
        """Initialize with label and blocksize.

        Args:
            zone_map (ClickableLabel): clickable QLabel
            block_size (int, optional): block size of grid. Defaults to BLOCK_SIZE.
        """
        self.width: int = 0
        self.height: int = 0
        self.block_size: int = block_size
        self.map = zone_map

    def clear(self, color: QColor = BACKGROUND_HEX) -> None:
        """Clears the map label.

        Args:
            color (QColor, optional): color. Defaults to BACKGROUND_HEX.
        """
        canvas = self.map.pixmap()
        canvas.fill(color)
        self.map.setPixmap(canvas)

    def draw_point(self, x: int, y: int, color: QColor, width: int) -> None:
        """Draw a point.

        Args:
            x (int): x-coordinate
            y (int): y-coordinate
            color (QColor): color
            width (int): point width
        """
        canvas = self.map.pixmap()
        painter = QtGui.QPainter(canvas)
        pen = QPen(color)
        pen.setWidth(width)
        painter.setPen(pen)
        painter.drawPoint(x, y)
        painter.end()
        self.map.setPixmap(canvas)

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, color: QColor) -> None:
        """Draw a line from point 1 to point 2 on the grid system.

        Args:
            x1 (int): Point 1 x-coordinate
            y1 (int): Point 1 y-coordinate
            x2 (int): Point 2 x-coordinate
            y2 (int): Point 2 y-coordinate
            color (QColor): color
        """
        canvas = self.map.pixmap()
        painter = QtGui.QPainter(canvas)
        painter.setPen(color)
        painter.drawLine(x1, y1, x2, y2)
        painter.end()
        self.map.setPixmap(canvas)

    def draw_text(self, text: str, x: int, y: int, color: QColor) -> None:
        """Write text at coordinates in grid system.

        Args:
            text (str): Text
            x (int): pixel x
            y (int): pixel y
            color (QColor): color
        """
        canvas = self.map.pixmap()
        painter = QtGui.QPainter(canvas)
        painter.setPen(color)
        painter.drawText(x, y, text)
        painter.end()
        self.map.setPixmap(canvas)

    def draw_grid_text(
        self, text: str, u: int, v: int, color: QColor = TEXT_HEX
    ) -> None:
        """Draw a text in the middle of a tile.

        Args:
            text (str): text
            u (int): x axis
            v (int): y axis
            color (QColor, optional): color. Defaults to TEXT_HEX.
        """
        x = u * self.block_size + self.block_size // 2
        y = v * self.block_size + self.block_size // 2
        self.draw_text(text, x, y, color)

    def draw_grid(self, width: int, height: int, color: QColor = GRID_HEX) -> None:
        """Draws a grid.

        Args:
            width (int): width in blocks
            height (int): height in blocks
            color (QColor, optional): color. Defaults to GRID_HEX.
        """
        self.width = width
        self.height = height
        block_size = self.block_size
        width_pixels = width * block_size + 1
        height_pixels = height * block_size + 1
        self.map.setFixedSize(width_pixels, height_pixels)
        self.map.setPixmap(QtGui.QPixmap(self.map.size()))

        # vertical lines
        for i in range(0, width + 1):
            x_i = i * block_size
            self.draw_line(x_i, 0, x_i, height * block_size, color)

        # horizontal lines
        for i in range(0, height + 1):
            y_i = i * block_size
            self.draw_line(0, y_i, width * block_size, y_i, color)

    def draw_grid_line(
        self, u1: int, v1: int, u2: int, v2: int, color: QColor = LINE_HEX
    ) -> None:
        """Draws a line from point 1 to 2 in grid system.

        Args:
            u1 (int): Point 1 u-coordinate
            v1 (int): Point 1 v-coordinate
            u2 (int): Point 2 u-coordinate
            v2 (int): Point 2 v-coordinate
            color (QColor, optional): color. Defaults to LINE_HEX.
        """
        self.draw_line(
            u1 * self.block_size + self.block_size // 2,
            v1 * self.block_size + self.block_size // 2,
            u2 * self.block_size + self.block_size // 2,
            v2 * self.block_size + self.block_size // 2,
            color,
        )

    def draw_grid_point(self, u: int, v: int, color: QColor = POINT_HEX) -> None:
        """Draw a point in the grid.

        Args:
            u (int): grid tile number in x axis, starting with 0
            v (int): grid tile number in y axis, starting with 0
            color (QColor, optional): color. Defaults to POINT_HEX.
        """
        width = self.block_size // 3
        x = u * self.block_size + self.block_size // 2
        y = v * self.block_size + self.block_size // 2
        self.draw_point(x, y, color, width)

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
