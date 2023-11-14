"""Test BaseConverter class."""
import json
import socket
from dataclasses import asdict

from ebl_coords.backend.converter.base_converter import BaseConverter
from ebl_coords.backend.converter.output_dataclass import ConverterOuput


def test_streaming() -> None:
    """Test connection to BaseConverter Server."""
    c1 = ConverterOuput(0, 1, 1, 1, {})
    c1_binary = json.dumps(asdict(c1)).encode()
    c2 = ConverterOuput(2, 3, 4, 5, {"key": 0.1})
    c2_binary = json.dumps(asdict(c2)).encode()
    c3 = ConverterOuput(3, 1, 1, 1, {})
    c3_binary = json.dumps(asdict(c3)).encode()

    ip = "127.0.0.1"
    port = 12701
    bc = BaseConverter(ip_server=ip, port_server=port)
    bc.buffer.put(c1)
    bc.buffer.put(c2)
    bc.buffer.put(c3)

    bc.alive.wait()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as recv_socket:
        recv_socket.connect((ip, port))
        reader = recv_socket.makefile("rb")
        c1_answer = reader.readline()
        c2_answer = reader.readline()
        c3_answer = reader.readline()

    assert c1_answer == c1_binary + b"\n"
    assert json.loads(c1_answer) == asdict(c1)

    assert c2_answer == c2_binary + b"\n"
    assert json.loads(c2_answer) == asdict(c2)

    assert c3_answer == c3_binary + b"\n"
    assert json.loads(c3_answer) == asdict(c3)
