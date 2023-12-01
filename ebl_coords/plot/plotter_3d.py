"""Module to plot tracks and wayspoints."""
from queue import Queue
from typing import List, Optional

import numpy as np
import pandas as pd
import pyvista as pv
from neo4j import GraphDatabase

from ebl_coords.backend.constants import NEO4J_PASSWD, NEO4J_URI, NEO4J_USR
from ebl_coords.backend.mock.gt_recorder_original import GtRecorderOriginal
from ebl_coords.backend.transform_data import filter_df
from ebl_coords.plot.helpers import get_cloud


class Plotter3d:
    """Pyvista based plotter."""

    def __init__(self, z_flg: bool = True, interactive_update: bool = False) -> None:
        """Initialize the Plotter.

        Args:
            z_flg (bool, optional): If False squish the z-axis to zero. Defaults to True.
            interactive_update (bool, optional): Set to true if plot from socket. Defaults to False.
        """
        self.z_flg = z_flg
        self.interactive_update = interactive_update
        self.session = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USR, NEO4J_PASSWD)
        ).session()

        pv.set_plot_theme("dark")
        self.title: Optional[str] = None
        self.pl = pv.Plotter()
        self.pl.enable_eye_dome_lighting()
        self.pl.add_axes()
        if self.interactive_update:
            self.pl.show(interactive_update=self.interactive_update)

        self.bhfs: List[str] = []
        self.ts_labels: np.ndarray
        self.ts_coords: np.ndarray

        self.rail_lines: np.ndarray

        self.waypoints: pd.DataFrame
        self.socket_buffer: Queue[np.ndarray] = Queue(0)

    def __del__(self) -> None:
        """Close neo4j session."""
        self.session.close()

    def _add_track_switches(self) -> None:
        """Add track switches from neo4j DB."""
        ts_coords = []
        ts_labels = []
        for bhf in self.bhfs:
            bhf = bhf.upper()
            cmd = f"MATCH (node:WEICHE {{bhf: '{bhf}'}} ) RETURN node.name, node.x, node.y, node.z"
            track_switches = self.session.run(cmd).data()
            for ts in track_switches[::2]:
                ts_labels.append(f"{bhf}_{ts['node.name']}")
                z = 0
                if self.z_flg:
                    z = ts["node.z"]
                ts_coords.append(
                    np.array([ts["node.x"], ts["node.y"], z], dtype=np.float32)
                )
            self.ts_coords = np.array(ts_coords, dtype=np.float32)
            self.ts_labels = np.array(ts_labels)

    def _rails_to_lines(self) -> None:
        """Collect all rails from DB and save the coordinates."""
        cmd = "MATCH (n1)-[TRAIN_RAIL]->(n2) RETURN n1, n2"
        lines = self.session.run(cmd).data()
        line_points = []
        for line in lines:
            n1 = line["n1"]
            n2 = line["n2"]
            p1 = np.array([n1["x"], n1["y"], n1["z"]], dtype=np.float32)
            p2 = np.array([n2["x"], n2["y"], n2["z"]], dtype=np.float32)
            if not self.z_flg:
                p1[2] = 0
                p2[2] = 0
            line_points.append([p1, p2])
        self.rail_lines = np.array(line_points).reshape(-1, 3)

    def plot_track_switches(
        self,
        bhfs: List[str],
        point_size: int = 15,
        point_color: str = "yellow",
        lines_color: Optional[str] = None,
    ) -> None:
        """Plot all track_switches.

        Args:
            bhfs (List[str]): list of trainstations.
            point_size (int, optional): point size. Defaults to 15.
            point_color (str, optional): color. Defaults to 'yellow'.
            lines_color (Optional[str], optional): If color, plot lines, which connect train switches. Defaults to None.
        """
        self.bhfs = list(map(lambda bhf: bhf.upper(), bhfs))
        self._add_track_switches()
        self.pl.add_point_labels(
            self.ts_coords,
            self.ts_labels,
            show_points=True,
            point_color=point_color,
            point_size=point_size,
            always_visible=True,
            render_points_as_spheres=True,
            font_size=10,
        )
        if lines_color:
            self._rails_to_lines()
            self.pl.add_lines(self.rail_lines, color=lines_color, width=3)

    def plot_waypoints_socket(self, ip: str, port: int, waypoints_file: str) -> None:
        """Plot live from GtCommand socket.

        Args:
            ip (str): ip of server
            port (int): port of server
            waypoints_file (str): write received GtCommand output into file.

        Raises:
            ConnectionRefusedError: interactive_update must be True.
        """
        if not self.interactive_update:
            raise ConnectionRefusedError(
                "Use only if Plotter is initialized with interactive-update = True"
            )
        recorder = GtRecorderOriginal(
            out_file=waypoints_file, ip=ip, port=port, plot_flg=True, notebook_flg=False
        )
        recorder.start_record()
        recorder.plot_points(pl=self.pl)

    def plot_waypoints_df(
        self,
        df: pd.DataFrame,
        kernel_size: Optional[int] = None,
        tolerance: Optional[int] = None,
    ) -> None:
        """Plot all points from DataFrame and preprocess them.

        Args:
            df (pd.DataFrame): df
            kernel_size (Optional[int], optional): kernel size of median filter. Defaults to None.
            tolerance (Optional[int], optional): minimal required distance to a neighbour. Defaults to None.
        """
        self.waypoints = filter_df(df, kernel_size=kernel_size, tolerance=tolerance)
        cloud = get_cloud(self.waypoints)
        if not self.z_flg:
            cloud.points[:, 2] = 0

        self.pl.add_points(cloud, render_points_as_spheres=True)
