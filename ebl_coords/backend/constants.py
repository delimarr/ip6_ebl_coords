"""Constants, server config."""
from os.path import abspath

from PyQt6.QtGui import QColor

# neo4j config
NEO4J_URI_LOCAL = "bolt://localhost:7687"
NEO4J_URI_CONTAINER = "bolt://neo4j:7687"
NEO4J_USR = "neo4j"
NEO4J_PASSWD = "password"

# gtcommand websocket serverside
GTCOMMAND_IP: str = "192.168.128.20"
GTCOMMAND_PORT: int = 18002
# GTCOMMAND_IP: str = "127.0.0.1"
# GTCOMMAND_PORT: int = 42042

# if true, set all z-coordinates to zero.
IGNORE_Z_AXIS: bool = True

# callback deltatime in ms, 30 Calls per Second
CPS: int = 30
CALLBACK_DT: int = 1000 // CPS

# zone dump file
ZONE_FILE: str = str(abspath("./zone_data/zone_dump.json"))

# config file
CONFIG_JSON: str = str(abspath("./ebl_config.json"))

# Net Config, always odd number
BLOCK_SIZE: int = 41
BLOCK_SIZE = BLOCK_SIZE // 2 * 2 + 1
GRID_LINE_WIDTH: int = 3

# domino colors
GRAY_HEX = QColor("#8F8F8F")
GREEN_HEX = QColor("#9ACC99")

BACKGROUND_HEX = QColor("#000000")  # black
GRID_HEX = QColor("#D3D3D3")  # light gray
POINT_HEX = QColor("#FFFFFF")  # white
LINE_HEX = QColor("#FFFFFF")  # white
TEXT_HEX = QColor("#FFFFFF")  # white
OCCUPIED_HEX = QColor("#FF0000")  # red
