"""Provide a simple socket connection to GtCommand."""
import socket
from threading import Thread
from typing import List

import numpy as np


class _InnerGtCommandApi:
    """GtCommand Api."""

    def __init__(self, ip: str = "127.0.0.1", port: int = 42042) -> None:
        """Initialize the buffer and the socket.

        Args:
            ip (str, optional): ip of GtCommand. Defaults to "127.0.0.1".
            port (int, optional): port of GtCommand. Defaults to 42042.
        """
        self.ip: str = ip
        self.port: int = port
        self.loc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer: List[np.ndarray] = []
        self.record_thread = Thread(target=self._record, daemon=True)

    def _record(self) -> None:
        buffer = b""
        self.loc_socket.connect((self.ip, self.port))
        while True:
            while b";" not in buffer:
                buffer += self.loc_socket.recv(1024)

            line, _, buffer = buffer.partition(b";")
            line_string = line.decode("utf-8")

            ds = line_string.split(",")
            point = np.array([ds[4], ds[5], ds[6]], dtype=np.float32)
            self.buffer.append(point)

    def start_record(self) -> None:
        """Start listening thread."""
        self.record_thread.start()


class GtCommandApi(_InnerGtCommandApi):
    """Singleton wrapper class for Api."""

    _api = None

    def __new__(cls, *args, **kwargs) -> _InnerGtCommandApi:  # type: ignore # pylint: disable=unused-argument
        """Return singleton or create if it does not exist yet."""
        if cls._api is None:
            cls._api = super(_InnerGtCommandApi, cls).__new__(cls)
        return cls._api
