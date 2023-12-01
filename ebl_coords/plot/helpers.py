"""Helperfunctions for pyvista plotting."""
from typing import Optional

import numpy as np
import pandas as pd
import pyvista as pv


def get_cloud(df: pd.DataFrame) -> pv.PolyData:
    """Get PolyData cloud from Dataframe and do sanity check.

    Args:
        df (pd.DataFrame): Dataframe containing x, y, z columns.

    Returns:
        pv.PolyData: pyvista cloud.
    """
    points = df[["x", "y", "z"]].to_numpy(dtype=np.float32)
    points = pv.pyvista_ndarray(points)
    cloud = pv.PolyData(points)
    np.allclose(points, cloud.points)
    return cloud


def quick_plot_3d(
    df: pd.DataFrame,
    title: str,
    colored: Optional[pd.Series] = None,
    z_flg: bool = True,
    lines_flg: bool = False,
) -> None:
    """Make 3d plot.

    Args:
        df (pd.DataFrame): Dataframe with GoT-Data
        title (str): title of plot
        colored (Optional[pd.Series], optional): if . Defaults to None.
        z_flg (bool): keep z-coords. Defaults is True.
        lines_flg (bool): draw lines between consecutive points. Defaults to False.
    """
    if not z_flg:
        df.loc[:, "z"] = 0

    cloud = get_cloud(df)
    if lines_flg:
        cloud = pv.lines_from_points(cloud.points)

    pv.set_plot_theme("dark")
    if colored is not None:
        if np.unique(colored).shape[0] == 2:
            cmap = ["red", "yellow"]
        else:
            cmap = ["hot"]
        cloud["point_color"] = colored
        pv.plot(
            cloud, cmap=cmap, scalars="point_color", eye_dome_lighting=True, text=title
        )
    else:
        pv.plot(cloud, eye_dome_lighting=True, text=title)
