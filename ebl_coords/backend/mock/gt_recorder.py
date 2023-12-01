"""Record GTCommand output and write to file. Execute only locally."""
import logging
import signal
import socket
import threading
from os import path
from queue import Queue
from typing import Optional, Tuple

import numpy as np
import pyvista as pv

from ebl_coords.backend.converter.helpers import now_ms


class GtRecorder:
    """Class to save in ConverterOutputFormat and plot live."""

    def __init__(
        self,
        out_file: str,
        ts_labels: np.ndarray,
        ts_coords: np.ndarray,
        max_rows: Optional[int] = None,
        ip: str = "127.0.0.1",
        port: int = 18002,
        plot_flg: bool = True,
        notebook_flg: bool = True,
        z_flg: bool = True,
    ) -> None:
        """Open and listen to a socket and write output to file. Hit CTRL + BREAK to stop.

        Args:
            out_file (str): path to a new output file
            ts_labels (np.ndarray): trainswitches labels
            ts_coords (np.ndarray): trainswitches coordinates
            ip (str, optional): ip adress server socket. Defaults to "127.0.0.1".
            max_rows (int, optional): Limits how many lines will be received. Defaults to None.
            port (int, optional): port server socket. Defaults to 18002.
            plot_flg (bool, optional): Plot each 5th point live. Defaults to True.
            notebook_flg (bool, optional): Set to True if executing in Notebook. Defaults to True.
            z_flg (bool, optional): True to keep z-axis. Defaults to True.
        """
        self.out_file = path.abspath(out_file)
        self.max_rows = max_rows
        self.ts_labels = ts_labels
        self.ts_coords = ts_coords
        self.z_flg = z_flg
        self.fd = open(self.out_file, "x", encoding="utf-8")
        self.loc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.plot_flg = plot_flg
        self.buffer: Queue[np.ndarray] = Queue(0)
        self.switch_track_buffer: Queue[Tuple[np.ndarray, np.ndarray]] = Queue(0)
        self.notebook_flg = notebook_flg
        self.record_thread = threading.Thread(target=self.record, daemon=False)
        self.stop_recording = threading.Event()
        signal.signal(signal.SIGINT, self._handler)

        self.threshold = 30

    def _handler(self, signum: int, frame) -> None:  # type: ignore
        if not self.stop_recording.is_set():
            self.stop_recording.set()
            logging.debug("%s, %s", signum, frame)

    def plot_points(self, pl: pv.Plotter = None) -> None:
        """Plot every 5th point.

        pl (pv.Plotter, optional): Existing Plotter to add point, None = create new one. Defaults to None.
        """
        if not pl:
            pl = pv.Plotter(notebook=self.notebook_flg)
        pl.add_axes()
        pl.enable_eye_dome_lighting()
        pl.show(interactive_update=True)

        logging.debug("start plotting...")
        while self.record_thread.is_alive():
            if not self.buffer.empty():
                point = self.buffer.get()
                pl.add_points(point)
            if not self.switch_track_buffer.empty():
                labels, point = self.switch_track_buffer.get()
                points = np.resize(point, (labels.shape[0], 3))
                pl.add_point_labels(
                    points,
                    labels,
                    show_points=True,
                    point_color="blue",
                    point_size=self.threshold,
                    always_visible=True,
                    render_points_as_spheres=True,
                    font_size=10,
                )
            pl.update()

    def start_record(self) -> None:
        """Start listening thread."""
        self.record_thread.start()

    def record(self) -> None:
        """Listen on socket, fill the buffer and write to file."""
        self.loc_socket.connect((self.ip, self.port))

        i = 0
        logging.debug("start recording...")
        buffer = b""
        while self.max_rows is None or i < self.max_rows:
            while b";" not in buffer:
                buffer += self.loc_socket.recv(1024)

            line, _, buffer = buffer.partition(b";")
            line_string = line.decode("utf-8")
            self.fd.write(str(now_ms()) + ";")
            self.fd.writelines(line_string + ";\n")
            if i % 5 == 0:
                ds = line_string.split(",")
                point = np.array([ds[4], ds[5], ds[6]], dtype=np.float32)
                if not self.z_flg:
                    point[2] = 0
                self.buffer.put(point)

            logging.info("New point: %d", i)
            i += 1
            if self.stop_recording.is_set():
                self.fd.close()
                logging.info("%s properly closed.", self.out_file)
                break
