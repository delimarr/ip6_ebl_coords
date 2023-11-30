"""Save and plot input from gtcommand."""
import signal
import sys
from os import path

from ebl_coords.backend.mock.gt_recorder_original import GtRecorderOriginal

folder = "./data/got_raw_files/run10/"

# out_file='dab_ew01_dcc019'
# out_file='dab_ew02_dcc017'
# out_file='dab_ew03_dcc018'
# out_file='dab_ew04_dcc013'
# out_file='dab_ew05_dcc014'
# out_file='dab_ew06_dcc016'
out_file = "dab_ew07_dcc015"
# out_file='dab_ew08_dcc003'
# out_file='dab_ew09_dcc004'
# out_file='dab_ew10_dcc001'
# out_file='dab_ew11_dcc002'
# out_file='dab_ew12_dcc007'
# out_file='dab_ew13_dcc006'
# out_file = "dab_ew14_dcc005"
port = 18002

c = GtRecorderOriginal(
    out_file=path.join(folder, out_file), port=port, notebook_flg=False, max_rows=200
)


def handler(signum, frame) -> None:
    """Terminate the script with CTRL + C."""
    global c
    del c
    sys.exit(0)


signal.signal(signal.SIGINT, handler)
c.start_record()
c.plot_points()
