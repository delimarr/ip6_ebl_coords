"""Notebook_init test."""

import pyvista as pv

from ebl_coords.backend import notebook_init  # noqa pylint:disable=unused-import


def test_xserver() -> None:
    """Test if pyvista plotter throws no warning."""
    _ = pv.Plotter()
