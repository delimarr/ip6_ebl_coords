"""Constants used in the Notebooks and tvData.py."""
from os.path import abspath

# neo4j config
NEO4J_URI_LOCAL = "bolt://localhost:7687"
NEO4J_URI_CONTAINER = "bolt://neo4j:7687"
NEO4J_USR = "neo4j"
NEO4J_PASSWD = "password"

ECOS_IP = None  # HAVE TO LOOK UP
ECOS_PORT = None  # SAME

TOLERANCE: int = 30
SCALE: float = 0.2
LOWER_BND: int = -180
UPPER_BND: int = 560

DUMP: str = abspath("./data/dump/")

FILES_S4 = [
    "gr_ringstrecke_s4_04",
    "gr_ringstrecke_s4_05",
    "gr_ringstrecke_s4_06",
    "gr_ringstrecke_s4_07",
    "gr_ringstrecke_s4_08",
    "gr_ringstrecke_s4_09",
    "gr_ringstrecke_s4_10",
    "gr_ringstrecke_s4_11",
    "gr_ringstrecke_s4_12",
    "gr_ringstrecke_s4_13",
    "gr_ringstrecke_s4_14",
]

BEST_S4 = "gr_ringstrecke_s4_06"
