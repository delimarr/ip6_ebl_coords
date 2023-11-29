"""Record GTCommand output and write to file. Execute only locally."""
import json
import socket
import threading
from os import path
from queue import Queue
from typing import Optional

import numpy as np
import pyvista as pv

from ebl_coords.backend.converter.converter_output import ConverterOuput


class GtRecorder:
    """Class to save in ConverterOutputFormat and plot live."""

    def __init__(
        self,
        out_file: str,
        max_rows: Optional[int] = None,
        ip: str = "127.0.0.1",
        port: int = 18002,
        plot_flg: bool = True,
        notebook_flg: bool = True,
    ) -> None:
        """Open and listen to a socket and write output to file. Hit CTRL + BREAK to stop.

        Args:
            out_file (str): path to a new output file
            ip (str, optional): ip adress server socket. Defaults to "127.0.0.1".
            max_rows (int, optional): Limits how many lines will be received. Defaults to None.
            port (int, optional): port server socket. Defaults to 18002.
            plot_flg (bool, optional): Plot each 5th point live. Defaults to True.
            notebook_flg (bool, optional): Set to True if executing in Notebook. Defaults to True.
        """
        self.out_file = path.abspath(out_file)
        self.max_rows = max_rows
        self.fd = open(self.out_file, "x", encoding="utf-8")
        self.loc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.plot_flg = plot_flg
        self.buffer: Queue[ConverterOuput] = Queue(0)
        self.notebook_flg = notebook_flg
        self.record_thread = threading.Thread(target=self.record, daemon=True)

    def plot_points(self) -> None:
        """Plot every 5th point."""
        pl = pv.Plotter(notebook=self.notebook_flg)
        pl.add_axes()
        pl.enable_eye_dome_lighting()
        pl.show(interactive_update=True)

        i = 0
        print("start plotting...")
        while True:
            if not self.buffer.empty():
                converter_output = self.buffer.get()
                if i % 5 == 0:
                    point = pv.pyvista_ndarray(
                        np.array(
                            [
                                converter_output.x,
                                converter_output.y,
                                converter_output.z,
                            ],
                            dtype=np.float32,
                        )
                    )
                    pl.add_points(point)
                    print(self.buffer.qsize())
                i += 1
            pl.update()

    def start_record(self) -> None:
        """Start listening thread."""
        self.record_thread.start()

    def __del__(self) -> None:
        """Close file descriptor and socket."""
        print("\nclosing...")
        self.fd.close()

    def record(self) -> None:
        """Listen on socket, fill the buffer and write to file."""
        self.loc_socket.connect((self.ip, self.port))
        reader = self.loc_socket.makefile("rb")

        i = 0
        print("start recording...")
        while self.max_rows is None or i < self.max_rows:
            c_dict = json.loads(reader.readline())
            c = ConverterOuput(**c_dict)
            self.buffer.put(c)
            self.fd.write(str(c_dict) + ";\n")
            i += 1

        del self
