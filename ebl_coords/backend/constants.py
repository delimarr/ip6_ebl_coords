"""Constants, server config."""
from os.path import abspath
from threading import RLock

from PyQt6.QtGui import QColor

# live or mock
MOCK_FLG: bool = True

# neo4j config
NEO4J_URI_LOCAL: str = "bolt://localhost:7687"
NEO4J_URI_CONTAINER: str = "bolt://neo4j:7687"
NEO4J_USR: str = "neo4j"
NEO4J_PASSWD: str = "password"

# gtcommand websocket serverside
GTCOMMAND_IP: str = "192.168.128.20"
GTCOMMAND_PORT: int = 18002
if MOCK_FLG:
    GTCOMMAND_IP = "127.0.0.1"
    GTCOMMAND_PORT = 42042

# if true, set all z-coordinates to zero.
IGNORE_Z_AXIS: bool = True

# minimal distance [m] delta needed for summation
MIN_DELTA_DISTANCE: float = 0.03
MIN_SHOW_DISTANCE: float = 0.1

# GTCommand train switch hit threshold
TS_HIT_THRESHOLD: int = 50

# callback deltatime in ms, 30 Calls per Second
CPS: int = 60
CALLBACK_DT_MS: int = 1000 // CPS

# zone dump file
ZONE_FILE: str = str(abspath("./zone_data/zone_dump.json"))

# config file
CONFIG_JSON: str = str(abspath("./ebl_config.json"))

# Net Config, always odd number
BLOCK_SIZE: int = 41
BLOCK_SIZE = BLOCK_SIZE // 2 * 2 + 1
GRID_LINE_WIDTH: int = 3

# domino colors
GRAY_HEX: QColor = QColor("#8F8F8F")
GREEN_HEX: QColor = QColor("#9ACC99")

BACKGROUND_HEX: QColor = QColor("#000000")  # black
GRID_HEX: QColor = QColor("#D3D3D3")  # light gray
POINT_HEX: QColor = QColor("#FFFFFF")  # white
LINE_HEX: QColor = QColor("#FFFFFF")  # white
TEXT_HEX: QColor = QColor("#FFFFFF")  # white
OCCUPIED_HEX: QColor = QColor("#FF0000")  # red

# ecos df lock
ECOS_DF_LOCK = RLock()
