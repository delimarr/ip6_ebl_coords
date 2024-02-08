"""Provide a simple socket connection to GtCommand."""
from __future__ import annotations

import socket
from threading import Thread
from typing import TYPE_CHECKING

import numpy as np

from ebl_coords.backend.constants import GTCOMMAND_IP, GTCOMMAND_PORT, IGNORE_Z_AXIS
from ebl_coords.backend.observable.subject import Subject
from ebl_coords.backend.transform_data import get_tolerance_mask, get_track_switches_hit
from ebl_coords.decorators import override
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem
from ebl_coords.graph_db.graph_db_api import GraphDbApi

if TYPE_CHECKING:
    from ebl_coords.backend.observable.observer import Observer


class _InnerGtCommandSubject(Subject):
    """GtCommand Subject."""

    def __init__(
        self,
        median_kernel_size: int = 11,
        noise_filter_threshold: int = 30,
        ip: str = GTCOMMAND_IP,
        port: int = GTCOMMAND_PORT,
        ts_hit_threshold: int = 35,
    ) -> None:
        """Initialize the buffer and the socket.

        Args:
            median_kernel_size (int, optional): kernel size used for median filter. Defaults to 11.
            noise_filter_threshold (int, optional): Maximal allowed distance between neighbouring points. Defaults to 30.
            ip (str, optional): ip of GtCommand. Defaults to GTCOMMAND_IP.
            port (int, optional): port of GtCommand. Defaults to GTCOMMAND_PORT.
            ts_hit_threshold(int, optional): Maximal distance coord to trainswitch to be considered valid hit. Defaults to 35.
        """
        self.graph_db = GraphDbApi()
        self.ts_coords: np.ndarray
        self.ts_labels: np.ndarray | None = None
        self.ip: str = ip
        self.port: int = port
        self.ts_hit_threshold = ts_hit_threshold
        self.loc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.record_thread = Thread(
            target=self._record,
            daemon=True,
            args=[noise_filter_threshold],
        )
        self.record_thread.start()

        self.measure_observers: list[Observer] = []
        self.coords_observers: list[Observer] = []
        self.ts_hit_observers: list[Observer] = []

        self._noise_buffer = np.empty((3, 3), dtype=np.int32)
        self._median_buffer = np.empty((median_kernel_size, 3), dtype=np.int32)

    def set_next_ts(self, edge_id: str) -> None:
        """Set coordinates and label of following node after this edge.

        Args:
            edge_id (str): edge_id
        """
        weiche = SwitchItem.WEICHE.name
        cmd = f"""
        MATCH ({weiche})-[r]->(n:{weiche})\
        WHERE r.edge_id='{edge_id}'\
        RETURN n.node_id, n.x, n.y, n.z
        """
        df = self.graph_db.run_query(cmd)
        self.ts_coords = df[["n.x", "n.y", "n.z"]].to_numpy().astype(np.float32)
        if IGNORE_Z_AXIS:
            self.ts_coords[:, 2] = 0
        self.ts_labels = df["n.node_id"].to_numpy()

    def _filter_coord(
        self, coord: np.ndarray, noise_filter_threshold: int
    ) -> np.ndarray | None:
        med_coord: np.ndarray | None = None
        self._noise_buffer[-1] = coord
        if get_tolerance_mask(self._noise_buffer, noise_filter_threshold)[0]:
            self._median_buffer[-1] = self._noise_buffer[1]
            if not np.isnan(self._median_buffer).any():
                med_coord = np.median(self._median_buffer, axis=0)
            self._median_buffer = np.roll(
                self._median_buffer, shift=self._median_buffer.size - 3
            )

        self._noise_buffer = np.roll(
            self._noise_buffer, shift=self._noise_buffer.size - 3
        )
        return med_coord

    def _record(self, noise_filter_threshold: int) -> None:
        buffer = b""
        self.loc_socket.connect((self.ip, self.port))
        last_coord: np.ndarray | None = None
        ts_last_hit: np.ndarray | None = None
        while True:
            while b";" not in buffer:
                buffer += self.loc_socket.recv(1024)

            line, _, buffer = buffer.partition(b";")
            line_string = line.decode("utf-8")

            ds = line_string.split(",")
            coord = np.array([ds[4], ds[5], ds[6]], dtype=np.int32)
            filtered_coord = self._filter_coord(coord, noise_filter_threshold)
            if filtered_coord is not None and not np.any(filtered_coord == last_coord):
                self.notify(self.measure_observers, filtered_coord)
                if IGNORE_Z_AXIS:
                    filtered_coord[2] = 0
                self.notify(self.coords_observers, filtered_coord)
                if self.ts_labels and self.ts_hit_observers:
                    hit_labels = get_track_switches_hit(
                        self.ts_labels,
                        self.ts_coords,
                        filtered_coord.reshape(1, -1),
                        self.ts_hit_threshold,
                    )
                    last_coord = filtered_coord
                    if not np.any(ts_last_hit == hit_labels) and hit_labels.size > 0:
                        self.notify(self.ts_hit_observers, hit_labels)
                        ts_last_hit = hit_labels
                        print("hit")

    @override
    def attach(self, observer: Observer) -> None:
        """Attach observer.

        Args:
            observer (Observer): observer
        """
        observer_name = observer.__class__.__name__
        if observer_name == "TsMeasureObserver":
            self.measure_observers.append(observer)
        elif observer_name == "TsHitObserver":
            self.ts_hit_observers.append(observer)
        observer.subject = self

    @override
    def detach(self, observer: Observer) -> None:
        """Detach observer.

        Args:
            observer (Observer): observer
        """
        observer_name = observer.__class__.__name__
        if observer_name == "TsMeasureObserver":
            self.measure_observers.remove(observer)
        elif observer_name == "TsHitObserver":
            self.ts_hit_observers.remove(observer)


class GtCommandSubject(_InnerGtCommandSubject):
    """Singleton wrapper class for Subject."""

    _api = None

    def __new__(cls, *args, **kwargs) -> _InnerGtCommandSubject:  # type: ignore # pylint: disable=unused-argument
        """Return singleton or create if it does not exist yet."""
        if cls._api is None:
            cls._api = super(_InnerGtCommandSubject, cls).__new__(cls)
        return cls._api
