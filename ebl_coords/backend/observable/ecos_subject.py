"""Ecos Subject."""
from __future__ import annotations

import re
import socket
from threading import Thread
from typing import TYPE_CHECKING, Any

from ebl_coords.backend.observable.observer import Observer
from ebl_coords.backend.observable.subject import Subject
from ebl_coords.decorators import override

if TYPE_CHECKING:
    import pandas as pd


class _InnerEcosSubject(Subject):
    """Connect to ecos devices and provide observer pattern.

    Args:
        Subject (_type_): interface
    """

    def __init__(self, ecos_config: dict[str, Any], ecos_ids: pd.Series) -> None:
        """Initialize ecos subject.

        Args:
            ecos_config (dict[str, Any]): ecos config
            ecos_ids (pd.Series): all ecos ids in the network
        """
        self.ecos_config = ecos_config
        self.ecos_ids = ecos_ids
        self.observers: list[Observer] = []

    @override
    def attach(self, observer: Observer) -> None:
        """Attach an observer.

        Args:
            observer (Observer): observer
        """
        self.observers.append(observer)

    @override
    def detach(self, observer: Observer) -> None:
        """Detach an observer.

        Args:
            observer (Observer): observer
        """
        self.observers.remove(observer)

    def _record(self, ip: str, port: int) -> None:
        """Open and subsribe to an ecos socket. Notify observers.

        Args:
            ip (str): ecos ip
            port (int): ecos port
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as skt:
            skt.connect((ip, port))

            for ecos_id in self.ecos_ids:
                cmd = f"request({ecos_id}, view)"
                skt.sendall(cmd.encode("utf-8"))

            buffer = b""
            delimiter = b"<END 0 (OK)>"
            state_pattern = r"state\[(\d)\]"
            id_pattern = r"<EVENT (\d+)>"
            while True:
                while delimiter not in buffer:
                    buffer += skt.recv(1024)

                data, _, buffer = buffer.partition(delimiter)
                data_string = data.decode("utf-8")
                data_string.replace("\r\n", "")

                match_state = re.search(state_pattern, data_string)
                if match_state:
                    state = match_state.group(1)
                    match_id = re.search(id_pattern, data_string)
                    if match_id:
                        ecos_id = match_id.group(1)
                        self.notify(
                            self.observers,
                            {"id": int(ecos_id), "ip": ip, "state": int(state)},
                        )

    def start_record(self) -> None:
        """Start all ecos sockets in threads."""
        port = self.ecos_config["port"]
        for ip in self.ecos_config["bpk_ip"].values():
            Thread(target=self._record, args=[ip, port], daemon=True).start()


class EcosSubject(_InnerEcosSubject):
    """Singleton wrapper class for Subject."""

    _api = None

    def __new__(cls, *args, **kwargs) -> _InnerEcosSubject:  # type: ignore # pylint: disable=unused-argument
        """Return singleton or create if it does not exist yet."""
        if cls._api is None:
            cls._api = super(_InnerEcosSubject, cls).__new__(cls)
        return cls._api
