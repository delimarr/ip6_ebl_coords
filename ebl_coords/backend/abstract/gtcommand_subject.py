"""Subject of observerpattern in order to subscribe to gtcommand changes."""
from __future__ import annotations

from threading import Thread
from typing import TYPE_CHECKING

import numpy as np

from ebl_coords.backend.abstract.subject import Subject
from ebl_coords.backend.gtcommand.api import GtCommandApi
from ebl_coords.decorators import override
from ebl_coords.graph_db.api import Api as GraphApi
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem

if TYPE_CHECKING:
    from ebl_coords.backend.abstract.observer import Observer


class GtCommandSubject(Subject):
    """GtCommand Subject class.

    Args:
        Subject (_type_): Subject interface
    """

    def __init__(self, ip: str, port: int, graph_db: GraphApi) -> None:
        """Initialize GtCommandApi Singleton.

        Args:
            ip (str): ip GtCommand
            port (int): port GtCommand
            graph_db (GraphApi): graph db connection
        """
        self.ts_coords: np.ndarray

        self.next_coord: np.ndarray

        self.ts_hit_guid: str

        self.graph_db = graph_db

        self.measure_observers: list[Observer] = []
        self.ts_hit_observers: list[Observer] = []

        self.gt_command = GtCommandApi(ip, port)
        self.gt_command.start_record()

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

    def _measure_ts(self, selected_ts: str) -> None:
        self.gt_command.buffer = []
        while len(self.gt_command.buffer) < 150:
            pass
        coords = np.array(self.gt_command.buffer, dtype=np.float32)
        ts_coord = np.median(coords, axis=0)
        double_vertex = EdgeRelation.DOUBLE_VERTEX.name
        weiche = SwitchItem.WEICHE.name
        cmd = f"""
        MATCH(n1:WEICHE{{node_id:'{selected_ts}'}})-[:{double_vertex}]->(n2:{weiche})\
        SET n1.x = '{ts_coord[0]}'\
        SET n2.x = '{ts_coord[0]}'\
        SET n1.y = '{ts_coord[1]}'\
        SET n2.y = '{ts_coord[1]}'\
        SET n1.z = '{ts_coord[2]}'\
        SET n2.z = '{ts_coord[2]}';
        """
        self.graph_db.run_query(cmd)
        self.notify(self.measure_observers, ts_coord)

    def measure_ts(self, selected_ts: str) -> None:
        """Start measurement of trainswitch in a new thread.

        Args:
            selected_ts (str): guid of trainswitch
        """
        Thread(target=self._measure_ts, daemon=True, args=[selected_ts]).start()
