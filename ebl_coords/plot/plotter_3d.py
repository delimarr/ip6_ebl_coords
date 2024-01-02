"""Module to plot tracks and wayspoints."""
from queue import Queue
from typing import Optional

import numpy as np
import pandas as pd
import pyvista as pv

from ebl_coords.backend.mock.gt_recorder import GtRecorder
from ebl_coords.backend.mock.gt_recorder_filtered import GTRecorderFiltered
from ebl_coords.backend.transform_data import filter_df, get_track_switches_hit
from ebl_coords.graph_db.api import Api
from ebl_coords.plot.helpers import get_cloud


class Plotter3d:
    """Pyvista based plotter."""

    def __init__(
        self,
        kernel_size: int,
        tolerance: int,
        z_flg: bool = True,
        interactive_update: bool = False,
        ts_threshold: int = 30,
        track_flg: bool = False,
    ) -> None:
        """Initialize the Plotter.

        Args:
            z_flg (bool, optional): If False squish the z-axis to zero. Defaults to True.
            interactive_update (bool, optional): Set to true if plot from socket. Defaults to False.
            kernel_size (int): kernel_size of median filter, must be odd.
            tolerance (int): minimal distance to closest neighbour waypoint needed to be valid.
            ts_threshold (int, optional): Minimal distance required to be in around train switches. Defaults to 30.
            track_flg (bool, optional): track the distance and the velocity. Defaults to False.
        """
        self.z_flg = z_flg
        self.interactive_update = interactive_update
        self.kernel_size = kernel_size
        self.tolerance = tolerance
        self.ts_threshold = ts_threshold
        self.track_flg = track_flg
        self.graph_db = Api()

        pv.set_plot_theme("dark")
        self.title: Optional[str] = None
        self.pl = pv.Plotter()
        self.pl.enable_eye_dome_lighting()
        self.pl.add_axes()
        if self.interactive_update:
            self.pl.show(interactive_update=self.interactive_update, full_screen=True)

        self.ts_labels: np.ndarray
        self.ts_coords: np.ndarray

        self.rail_lines: np.ndarray

        self.waypoints: pd.DataFrame
        self.socket_buffer: Queue[np.ndarray] = Queue(0)

    def _add_track_switches(self) -> None:
        """Add track switches from neo4j DB."""
        cmd = "MATCH (node:WEICHE) RETURN node.bhf, node.name, node.x, node.y, node.z"
        df = self.graph_db.run_query(cmd)[::2]
        self.ts_labels = (df["node.bhf"] + "_" + df["node.name"]).to_numpy()
        self.ts_coords = df[["node.x", "node.y", "node.z"]].to_numpy(dtype=np.float32)
        if not self.z_flg:
            self.ts_coords[:, 2] = 0

    def _rails_to_lines(self) -> None:
        """Collect all rails from DB and save the coordinates."""
        cmd = "MATCH (n1)-[:TRAIN_RAIL]->(n2) RETURN n1.x, n1.y, n1.z, n2.x, n2.y, n2.z"
        df = self.graph_db.run_query(cmd)
        self.rail_lines = df.to_numpy(dtype=np.float32).reshape(-1, 3)
        if not self.z_flg:
            self.rail_lines[:, 2] = 0

    def plot_track_switches(
        self,
        point_size: int = 15,
        point_color: str = "yellow",
        lines_color: Optional[str] = None,
    ) -> None:
        """Plot all track_switches.

        Args:
            point_size (int, optional): point size. Defaults to 15.
            point_color (str, optional): color. Defaults to 'yellow'.
            lines_color (Optional[str], optional): If color, plot lines, which connect train switches. Defaults to None.
        """
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

        self.pl.view_xy()

    def plot_waypoints_socket(self, ip: str, port: int, waypoints_file: str) -> None:
        """Plot live from GtCommand socket. If kernel_size and tolerance is set, preprcess coordinates.

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

        if self.kernel_size and self.tolerance:
            recorder = GTRecorderFiltered(
                out_file=waypoints_file,
                ip=ip,
                port=port,
                plot_flg=True,
                notebook_flg=False,
                kernel_size=self.kernel_size,
                tolerance=self.tolerance,
                ts_labels=self.ts_labels,
                ts_coords=self.ts_coords,
                z_flg=self.z_flg,
            )
        else:
            recorder = GtRecorder(  # type: ignore
                out_file=waypoints_file,
                ip=ip,
                port=port,
                plot_flg=True,
                notebook_flg=False,
                ts_labels=self.ts_labels,
                ts_coords=self.ts_coords,
                z_flg=self.z_flg,
                ts_threshold=self.ts_threshold,
            )
        recorder.start_record()
        recorder.plot_points(pl=self.pl)

    def plot_waypoints_df(
        self,
        df: pd.DataFrame,
    ) -> None:
        """Plot all points from DataFrame and preprocess them.

        Args:
            df (pd.DataFrame): df
        """
        self.waypoints = filter_df(
            df, kernel_size=self.kernel_size, tolerance=self.tolerance
        )
        cloud = get_cloud(self.waypoints)
        if not self.z_flg:
            cloud.points[:, 2] = 0

        hit = get_track_switches_hit(
            self.ts_labels, self.ts_coords, cloud.points, self.ts_threshold
        )
        mask = np.isin(self.ts_labels, hit)

        self.pl.add_point_labels(
            self.ts_coords[mask],
            self.ts_labels[mask],
            show_points=True,
            point_color="#FF64B5F6",
            point_size=30,
            always_visible=True,
            render_points_as_spheres=True,
            font_size=10,
        )
        print(self.ts_labels[mask])

        self.pl.add_points(cloud, render_points_as_spheres=True)
        self.pl.show()
