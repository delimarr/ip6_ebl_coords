"""Plotter example."""
import os
import threading

from ebl_coords.backend.converter.replay_converter import ReplayConverter
from ebl_coords.plot.plotter_3d import Plotter3d


def replay():
    """Replay raw got files to socket."""
    folder = "./data/got_raw_files/run8/"
    files = os.listdir(folder)
    rp = ReplayConverter(
        files=files,
        folder=folder,
        raw_flg=True,
    )
    rp.read_input()


replay_thread = threading.Thread(target=replay, daemon=True)
replay_thread.start()

ip = "127.0.0.1"
port = 42042
folder = "./data/got_raw_files/"
files = os.listdir(folder)

p = Plotter3d(interactive_update=True, kernel_size=5, tolerance=20)
p.plot_track_switches(lines_color="white")
out_file = "temp.dat"
if os.path.exists(out_file):
    os.remove(out_file)
p.plot_waypoints_socket(ip, port, out_file)
