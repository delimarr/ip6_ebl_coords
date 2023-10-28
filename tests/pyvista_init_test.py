"""Notebook_init test."""

import pyvista as pv

from ebl_coords.backend import pyvista_init  # noqa pylint:disable=unused-import


def test_pyvista_init() -> None:
    """Test if pyvista plotter throws no warning."""
    _ = pv.Plotter()
