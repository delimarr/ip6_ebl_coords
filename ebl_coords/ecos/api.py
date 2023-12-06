"""Module to interact with ECoS."""
import logging
import socket
import threading
from queue import Queue

from ebl_coords.backend.constants import ECOS_IP, ECOS_PORT


class _InnerApi:
    """Class to interact with ECoS."""

    def __init__(self) -> None:
        """Initialize the API."""
        self.ecos_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_buffer: Queue[bytes]
        self.reply_buffer: Queue[bytes]
        self.ecos_thread = threading.Thread(
            target=self._ecos_socket_thread, daemon=False
        )

    def send_query(self, query: str) -> None:
        """Send query to ECoS.

        Args:
            query (str): query for ECoS
        """
        self.command_buffer.put(query.encode() + b"\n")

    def _ecos_socket_thread(self) -> None:
        """Send commands to socket and listen for replies."""
        self.ecos_socket.connect((ECOS_IP, ECOS_PORT))

        logging.debug("connected to ECoS")

        while True:
            if not self.command_buffer.empty():
                command = self.command_buffer.get()
                self.ecos_socket.sendall(command)

    def __del__(self) -> None:
        """Close websocket."""
        self.ecos_socket.close()


class Api(_InnerApi):
    """Singleton wrapper class for Api."""

    _api = None

    def __new__(cls) -> _InnerApi:  # type: ignore
        """Return singleton or create if it does not exist."""
        if cls._api is None:
            cls._api = super(_InnerApi, cls).__new__(cls)
        return cls._api
