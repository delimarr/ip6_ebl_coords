"""Constants, server config."""

# neo4j config
NEO4J_URI_LOCAL = "bolt://localhost:7687"
NEO4J_URI_CONTAINER = "bolt://neo4j:7687"
NEO4J_USR = "neo4j"
NEO4J_PASSWD = "password"

# gtcommand websocket serverside
# GTCOMMAND_IP: str = "192.168.128.50"
# GTCOMMAND_PORT: int = 18002
GTCOMMAND_IP: str = "127.0.0.1"
GTCOMMAND_PORT: int = 42042

# if true, set all z-coordinates to zero.
IGNORE_Z_AXIS: bool = True

# callback deltatime in ms, 30 FPS
CALLBACK_DT: int = 1000 // 30
