"""Draws Zones."""
from typing import List, Optional, Tuple

from PyQt6 import QtGui
from PyQt6.QtGui import QColor, QPen

from ebl_coords.backend.constants import BACKGROUND_HEX, BLOCK_SIZE, GRID_HEX
from ebl_coords.backend.constants import GRID_LINE_WIDTH, LINE_HEX, POINT_HEX, TEXT_HEX
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

    def draw_line(
        self, x1: int, y1: int, x2: int, y2: int, color: QColor, width: int = 1
    ) -> None:
        """Draw a line from point 1 to point 2 on the grid system.

        Args:
            x1 (int): Point 1 x-coordinate
            y1 (int): Point 1 y-coordinate
            x2 (int): Point 2 x-coordinate
            y2 (int): Point 2 y-coordinate
            color (QColor): color
            width (int): line width in pixel. Defaults to 1.
        """
        canvas = self.map.pixmap()
        painter = QtGui.QPainter(canvas)
        pen = QPen(color)
        pen.setWidth(width)
        painter.setPen(pen)
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
        self,
        u1: int,
        v1: int,
        u2: int,
        v2: int,
        snap_to_border: bool,
        color: QColor = LINE_HEX,
        width: int = GRID_LINE_WIDTH,
    ) -> None:
        """Draws a line from point 1 to 2 in grid system. Point 1 is the neutral point.

        Args:
            u1 (int): Point1 u-coordinate
            v1 (int): Point1 v-coordinate
            u2 (int): Point2 u-coordinate
            v2 (int): Point2 v-coordinate
            snap_to_border (Tuple[bool, bool]): snap points to rectangular border
            color (QColor, optional): color. Defaults to LINE_HEX.
            width (int): line width in pixel. Defaults to GRID_LINE_WIDTH.
        """
        x1: int
        y1: int
        if snap_to_border:
            border_coords = self.get_boundary_point(u1, v1, u2, v2)
            if border_coords:
                x1, y1 = border_coords
        else:
            x1 = u1 * self.block_size + self.block_size // 2
            y1 = v1 * self.block_size + self.block_size // 2

        x2 = u2 * self.block_size + self.block_size // 2
        y2 = v2 * self.block_size + self.block_size // 2
        self.draw_line(x1, y1, x2, y2, color, width)

    def _get_block_border_segments(
        self, u: int, v: int
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get line segment of border block.

        Args:
            u (int): left corner
            v (int): top corner

        Returns:
            List[Tuple[Tuple[int, int], Tuple[int, int]]]: [((p1.x, p1.y), (p2.x, p2.y)), ...]
        """
        top_l = (u * self.block_size, v * self.block_size)
        top_r = (u * self.block_size + self.block_size, v * self.block_size)
        bottom_l = (u * self.block_size, v * self.block_size + self.block_size)
        bottom_r = (
            u * self.block_size + self.block_size,
            v * self.block_size + self.block_size,
        )

        return [
            (top_l, top_r),
            (top_l, bottom_l),
            (bottom_r, top_r),
            (bottom_r, bottom_l),
        ]

    def get_boundary_point(
        self, u1: int, v1: int, u2: int, v2: int
    ) -> Optional[Tuple[int, int]]:
        """Return point on rect boundary around (u1, v1).

        https://gist.github.com/kylemcdonald/6132fc1c29fd3767691442ba4bc84018 [07.02.2024]

        Args:
            u1 (int): x-coordinate 1
            v1 (int): y-coordinate 1
            u2 (int): x-coordinate 2
            v2 (int): y-coordinate 2

        Returns:
            Optional[Tuple[int, int]]: coordinates
        """
        x1, y1 = self.get_pixel_coords(u1, v1)
        x2, y2 = self.get_pixel_coords(u2, v2)

        for b1, b2 in self._get_block_border_segments(u1, v1):
            b1_x, b1_y = b1
            b2_x, b2_y = b2
            denominator = (b2_y - b1_y) * (x2 - x1) - (b2_x - b1_x) * (y2 - y1)
            if denominator == 0:
                continue

            ua = (
                (b2_x - b1_x) * (y1 - b1_y) - (b2_y - b1_y) * (x1 - b1_x)
            ) / denominator
            if ua < 0 or ua > 1:  # out of range
                continue
            ub = ((x2 - x1) * (y1 - b1_y) - (y2 - y1) * (x1 - b1_x)) / denominator
            if ub < 0 or ub > 1:  # out of range
                continue
            x = x1 + ua * (x2 - x1)
            y = y1 + ua * (y2 - y1)
            return int(x), int(y)
        return None

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

    def get_pixel_coords(self, u: int, v: int) -> Tuple[int, int]:
        """Get pixel coordinates of grid coordinates.

        Args:
            u (int): u-coordinate
            v (int): v-coordinate

        Returns:
            Tuple[int, int]: x, y
        """
        x = u * self.block_size + self.block_size // 2
        y = v * self.block_size + self.block_size // 2
        return x, y
