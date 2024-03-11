"""Provide a simple socket connection to GtCommand."""
from __future__ import annotations

import socket
from threading import Thread
from typing import TYPE_CHECKING

import numpy as np

from ebl_coords.backend.constants import GTCOMMAND_IP, GTCOMMAND_PORT, IGNORE_Z_AXIS
from ebl_coords.backend.constants import TS_HIT_THRESHOLD
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
        ts_hit_threshold: int = TS_HIT_THRESHOLD,
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

        self.all_coord_observers: list[Observer] = []
        self.changed_coord_observers: list[Observer] = []
        self.ts_hit_observers: list[Observer] = []

        self._noise_buffer = np.full((3, 3), dtype=np.float32, fill_value=np.nan)
        self._median_buffer = np.full(
            (median_kernel_size, 3), dtype=np.float32, fill_value=np.nan
        )

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
            coord = np.array([ds[3], ds[4], ds[5]], dtype=np.int32)
            time_stamp = int(ds[0])
            filtered_coord = self._filter_coord(coord, noise_filter_threshold)
            if filtered_coord is not None:
                self.notify(self.all_coord_observers, filtered_coord)
                if not np.all(filtered_coord == last_coord):
                    if IGNORE_Z_AXIS:
                        filtered_coord[2] = 0
                    self.notify(
                        self.changed_coord_observers, (time_stamp, filtered_coord)
                    )
                    if self.ts_labels and self.ts_hit_observers:
                        hit_labels = get_track_switches_hit(
                            self.ts_labels,
                            self.ts_coords,
                            filtered_coord.reshape(1, -1),
                            self.ts_hit_threshold,
                        )
                        last_coord = filtered_coord
                        if (
                            not np.all(ts_last_hit == hit_labels)
                            and hit_labels.size > 0
                        ):
                            self.notify(self.ts_hit_observers, hit_labels)
                            ts_last_hit = hit_labels

    @override
    def attach(self, observer: Observer) -> None:
        """Attach observer.

        Args:
            observer (Observer): observer
        """
        self.changed_coord_observers.append(observer)

    def attach_all_coord(self, observer: Observer) -> None:
        """Attach observer that is notified whenever a new valid coordinate is received.

        observer.result contains the new coordinate as np.ndarray

        Args:
            observer (Observer): observer
        """
        observer.subject = self
        self.all_coord_observers.append(observer)

    def attach_changed_coord(self, observer: Observer) -> None:
        """Attach observer that is notified whenever a different coordinate is received.

        observer.result contains Tuple[int, np.ndarray] timestamp in ms, coordinate

        Args:
            observer (Observer): observer
        """
        observer.subject = self
        self.changed_coord_observers.append(observer)

    def attach_ts_hit(self, observer: Observer) -> None:
        """Attach observer that is notified whenever a train switch is hit.

        observer.result contains hit labels as np.ndarray

        Args:
            observer (Observer): observer
        """
        observer.subject = self
        self.ts_hit_observers.append(observer)

    def detach_all_coord(self, observer: Observer) -> None:
        """Detach observer from this hook.

        Args:
            observer (Observer): observer
        """
        self.all_coord_observers.remove(observer)

    def detach_changed_coord(self, observer: Observer) -> None:
        """Detach observer from this hook.

        Args:
            observer (Observer): observer
        """
        self.changed_coord_observers.remove(observer)

    def detach_ts_hit(self, observer: Observer) -> None:
        """Detach observer from this hook.

        Args:
            observer (Observer): observer
        """
        self.ts_hit_observers.remove(observer)

    @override
    def detach(self, observer: Observer) -> None:
        """Detach observer from all hooks.

        Args:
            observer (Observer): observer
        """
        if observer in self.all_coord_observers:
            self.all_coord_observers.remove(observer)
        if observer in self.changed_coord_observers:
            self.changed_coord_observers.remove(observer)
        if observer in self.ts_hit_observers:
            self.ts_hit_observers.remove(observer)


class GtCommandSubject(_InnerGtCommandSubject):
    """Singleton wrapper class for Subject."""

    _api = None

    def __new__(cls, *args, **kwargs) -> _InnerGtCommandSubject:  # type: ignore # pylint: disable=unused-argument
        """Return singleton or create if it does not exist yet."""
        if cls._api is None:
            cls._api = super(_InnerGtCommandSubject, cls).__new__(cls)
        return cls._api
