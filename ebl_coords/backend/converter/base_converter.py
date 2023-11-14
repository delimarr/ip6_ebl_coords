"""Receive any Input and stream it to a socket."""
import json
import socket
from dataclasses import asdict
from threading import Thread
from typing import List

from ebl_coords.backend.converter.output_dataclass import ConverterOuput


class BaseConverter:
    """Base Class for all converters."""

    def __init__(self, ip_server: str = "127.0.0.1", port_server: int = 42042) -> None:
        """Initialize converter base. Start server that streams from self.buffer.

        Args:
            ip_server (str): ip adress of output socket. Defaults to "127.0.0.1".
            port_server (int): port of output socket. Defaults to 42042.
        """
        self.ip_server: str = ip_server
        self.port_server: int = port_server

        self.buffer: List[ConverterOuput] = []

        self._start_streaming()

    def read_input(self) -> None:
        """Read Input and fill self.buffer.

        Raises:
            NotImplementedError: override this function.
        """
        raise NotImplementedError

    def _start_streaming(self) -> None:
        self.server_thread = Thread(
            target=self._stream_buffer,
            args=(self.ip_server, self.port_server),
            daemon=True,
        )
        self.server_thread.start()

    def _stream_buffer(self, ip: str, port: int) -> None:
        server_socket = socket.socket()
        server_socket.bind((ip, port))
        server_socket.listen(10)
        conn, _ = server_socket.accept()
        while True:
            if self.buffer:
                converter_output = self.buffer.pop()
                json_b = json.dumps(asdict(converter_output)).encode()
                conn.send(json_b)
