"""Test BaseConverter class."""
import socket
from time import sleep

from ebl_coords.backend.converter.base_converter import BaseConverter
from ebl_coords.backend.converter.output_dataclass import ConverterOuput


def test_streaming() -> None:
    """Test connection to BaseConverter Server."""
    c1 = ConverterOuput(0, 1, 1, 1, {})
    c2 = ConverterOuput(2, 3, 4, 5, {"key": 0.1})

    ip = "127.0.0.1"
    port = 12701
    bc = BaseConverter(ip_server=ip, port_server=port)

    sleep(0.1)

    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recv_socket.connect((ip, port))
    bc.buffer.append(c1)
    bc.buffer.append(c2)
    _ = recv_socket.recv(1024)
    _ = recv_socket.recv(1024)
    recv_socket.close()
