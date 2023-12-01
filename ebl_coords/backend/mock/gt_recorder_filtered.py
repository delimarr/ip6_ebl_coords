"""Postprocess the recorded points, before plotting."""
import logging
from typing import Optional

import numpy as np

from ebl_coords.backend.converter.helpers import now_ms
from ebl_coords.backend.mock.gt_recorder import GtRecorder
from ebl_coords.backend.transform_data import get_tolerance_mask


class GTRecorderFiltered(GtRecorder):
    """Save coordinates from GtCommand to file and plot them."""

    def __init__(
        self,
        out_file: str,
        kernel_size: int,
        tolerance: int,
        max_rows: Optional[int] = None,
        ip: str = "127.0.0.1",
        port: int = 18002,
        plot_flg: bool = True,
        notebook_flg: bool = False,
    ) -> None:
        """Initialize the recorder.

        Args:
            out_file (str): output file
            kernel_size (int): kernelsize for median filter, must be odd.
            tolerance (int): minimal distance required to a neighbour, in order for a point to be valid.
            max_rows (Optional[int], optional): Max rows written. Defaults to None.
            ip (str, optional): ip adress. Defaults to "127.0.0.1".
            port (int, optional): port. Defaults to 18002.
            plot_flg (bool, optional): Set False to avoid plotting. Defaults to True.
            notebook_flg (bool, optional): Set it to True, if working in a .ipynb. Defaults to False.
        """
        super().__init__(out_file, max_rows, ip, port, plot_flg, notebook_flg)
        self.kernel_size = kernel_size
        self.tolerance = tolerance

        self.tolerance_buffer = np.empty((3, 3), dtype=np.float32)
        self.median_buffer = np.empty((self.kernel_size, 3), dtype=np.float32)

    def record(self) -> None:
        """Listen on socket, fill the buffer and write to file."""
        self.loc_socket.connect((self.ip, self.port))

        rows = 0
        median_idx = 0
        plot_idx = 0
        logging.debug("start recording...")
        buffer = b""
        while self.max_rows is None or rows < self.max_rows:
            while b";" not in buffer:
                buffer += self.loc_socket.recv(1024)

            line, _, buffer = buffer.partition(b";")
            line_string = line.decode("utf-8")
            self.fd.write(str(now_ms()) + ";")
            self.fd.writelines(line_string + ";\n")
            ds = line_string.split(",")
            point = np.array([ds[4], ds[5], ds[6]], dtype=np.float32)

            self.tolerance_buffer[-1] = point
            if get_tolerance_mask(self.tolerance_buffer, self.tolerance)[0]:
                self.median_buffer[median_idx] = self.tolerance_buffer[1]
                median_idx += 1

            if median_idx == self.kernel_size:
                waypoint = np.median(self.median_buffer, axis=0)
                median_idx = self.kernel_size - 1
                self.median_buffer[0:-1, :] = self.median_buffer[1:, :]

                # add 5th point to plot buffer
                if plot_idx % 5 == 0:
                    self.buffer.put(waypoint)
                    plot_idx = 0
                else:
                    plot_idx += 1

            self.tolerance_buffer[0:2, :] = self.tolerance_buffer[1:3, :]

            logging.info("New point: %d", rows)
            rows += 1
            if self.stop_recording.is_set():
                self.fd.close()
                logging.info("%s properly closed.", self.out_file)
                break
