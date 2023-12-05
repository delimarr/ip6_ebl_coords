"""Postprocess the recorded points, before plotting."""
import logging
from typing import Optional

import numpy as np

from ebl_coords.backend.converter.helpers import now_ms
from ebl_coords.backend.mock.gt_recorder import GtRecorder
from ebl_coords.backend.transform_data import get_tolerance_mask, get_track_switches_hit


class GTRecorderFiltered(GtRecorder):
    """Save coordinates from GtCommand to file and plot them."""

    def __init__(
        self,
        out_file: str,
        kernel_size: int,
        tolerance: int,
        ts_labels: np.ndarray,
        ts_coords: np.ndarray,
        max_rows: Optional[int] = None,
        ip: str = "127.0.0.1",
        port: int = 18002,
        plot_flg: bool = True,
        notebook_flg: bool = False,
        z_flg: bool = True,
    ) -> None:
        """Initialize the recorder.

        Args:
            out_file (str): path to a new output file
            kernel_size (int): kernel size of median filter. Must be odd.
            tolerance (int): Min distance required to closest neighbour of a waypoint.
            ts_labels (np.ndarray): trainswitches labels
            ts_coords (np.ndarray): trainswitches coordinates
            ip (str, optional): ip adress server socket. Defaults to "127.0.0.1".
            max_rows (int, optional): Limits how many lines will be received. Defaults to None.
            port (int, optional): port server socket. Defaults to 18002.
            plot_flg (bool, optional): Plot each 5th point live. Defaults to True.
            notebook_flg (bool, optional): Set to True if executing in Notebook. Defaults to True.
            z_flg (bool, optional): True to keep z-axis. Defaults to True.
        """
        super().__init__(
            out_file,
            ts_labels,
            ts_coords,
            max_rows,
            ip,
            port,
            plot_flg,
            notebook_flg,
            z_flg,
        )
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
            if not self.z_flg:
                point[2] = 0

            self.tolerance_buffer[-1] = point
            if get_tolerance_mask(self.tolerance_buffer, self.tolerance)[0]:
                self.median_buffer[median_idx] = self.tolerance_buffer[1]
                median_idx += 1

            if median_idx == self.kernel_size:
                waypoint = np.median(self.median_buffer, axis=0)
                tracks_hit = get_track_switches_hit(
                    self.ts_labels,
                    self.ts_coords,
                    waypoints=[waypoint],
                    threshold=self.threshold,
                )
                if tracks_hit.size > 0:
                    self.switch_track_buffer.put((tracks_hit, waypoint))
                median_idx = self.kernel_size - 1
                self.median_buffer[0:-1, :] = self.median_buffer[1:, :]

                # add 5th point to plot buffer
                if plot_idx % 5 == 0:
                    ms = int(ds[1])
                    self.buffer.put((ms, waypoint))
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
