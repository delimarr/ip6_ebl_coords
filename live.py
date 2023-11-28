"""Save and plot input from file."""
import signal
import sys
import threading
from os import path, remove

from ebl_coords.backend.converter.replay_converter import ReplayConverter
from ebl_coords.backend.mock.gt_recorder import GtRecorder

folder = "./data/got_raw_files/run1/"
in_file = "gr_ringstrecke_s4_11"
out_file = "./tmp/test.dat"
assert path.exists(path.join(folder, in_file))
if path.exists(out_file):
    remove(out_file)

port = 18004

rc = ReplayConverter(folder=folder, files=[in_file], port_server=port)
stream = threading.Thread(target=rc.read_input, daemon=True)

global c
c = GtRecorder(out_file=out_file, port=port, notebook_flg=False)


def handler(signum, frame) -> None:
    """Terminate the script with CTRL + C."""
    global c
    del c
    sys.exit(0)


signal.signal(signal.SIGINT, handler)
stream.start()
c.start_record()
c.plot_points()
