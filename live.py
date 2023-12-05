"""Plotter example."""
import os
import threading
from os import environ

from ebl_coords.backend.converter.replay_converter import ReplayConverter
from ebl_coords.plot.plotter_3d import Plotter3d

if "DEV_CONTAINER" in environ:
    from ebl_coords.backend import pyvista_init  # noqa pylint:disable=unused-import


# 11 10 7 10 11 11 11 8 6 ; 9 ; 10 7 3 2
folder = "./data/got_raw_files/run8/"
files = [
    # "01_dab",
    "02_dab"
]


def replay():
    """Replay raw got files to socket."""
    rp = ReplayConverter(files=files, folder=folder, raw_flg=True, fixed_intervall=None)
    rp.read_input()


replay_thread = threading.Thread(target=replay, daemon=True)
replay_thread.start()

ip = "127.0.0.1"
port = 42042

"""
for file in files:
    p = Plotter3d(
        interactive_update=False,
        kernel_size=11,
        tolerance=50,
        z_flg=False
    )

    out_file = "temp.dat"
    if os.path.exists(out_file):
        os.remove(out_file)

    p.plot_track_switches(lines_color="white")
    p.plot_waypoints_df(get_df([file], folder))

"""
p = Plotter3d(
    interactive_update=True, kernel_size=11, tolerance=50, z_flg=False, ts_threshold=35
)
p.plot_track_switches(lines_color="white")
out_file = "temp.dat"
if os.path.exists(out_file):
    os.remove(out_file)
p.plot_waypoints_socket(ip, port, out_file)
