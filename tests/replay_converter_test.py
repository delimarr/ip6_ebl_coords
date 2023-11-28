"""Test ReplayConverter class."""

import json
import socket
from os.path import exists, join

import pytest

from ebl_coords.backend.converter.converter_output import ConverterOuput
from ebl_coords.backend.converter.replay_converter import ReplayConverter


@pytest.mark.timeout(3)  # type: ignore
def test_replay_converter() -> None:
    """Test if replay converter sends three rows."""
    folder = "./tests/test_data/"
    files = ["raw_got_test_file"]
    assert exists(join(folder, files[0]))

    ip = "127.0.0.1"
    port = 12702
    rc = ReplayConverter(ip_server=ip, port_server=port, folder=folder, files=files)
    rc.read_input()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as recv_socket:
        recv_socket.connect((ip, port))
        reader = recv_socket.makefile("rb")
        c1_answer = reader.readline()
        c2_answer = reader.readline()
        c3_answer = reader.readline()
    c1 = ConverterOuput(**json.loads(c1_answer))
    c2 = ConverterOuput(**json.loads(c2_answer))
    c3 = ConverterOuput(**json.loads(c3_answer))
    assert c1.x == 111
    assert c2.x == 222
    assert c3.x == 333
    assert len(c1.misc) == 45
