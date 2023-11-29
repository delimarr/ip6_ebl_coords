"""Save and plot input from gtcommand."""
import signal
import sys
from os import path

from ebl_coords.backend.mock.gt_recorder_original import GtRecorderOriginal

folder = "./data/got_raw_files/run8/"
out_file = "16_dab"

port = 18002

c = GtRecorderOriginal(
    out_file=path.join(folder, out_file), port=port, notebook_flg=False
)


def handler(signum, frame) -> None:
    """Terminate the script with CTRL + C."""
    global c
    del c
    sys.exit(0)


signal.signal(signal.SIGINT, handler)
c.start_record()
c.plot_points()
