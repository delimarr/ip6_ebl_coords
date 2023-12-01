"""Start X-Server for notebook rendering."""

from os import environ

import pyvista as pv

if "DEV_CONTAINER" in environ:
    pv.start_xvfb()
