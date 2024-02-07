"""Provide ecos scraper and config loader."""
import json
import socket
from typing import Any, Dict, List, Tuple

import pandas as pd


def load_config(config_file: str) -> Tuple[List[str], Dict[str, Any]]:
    """Load ecos json config file.

    Args:
        config_file (str): path with filename

    Returns:
        Tuple[List[str], Dict[str, Any]]: bkps, ecos
    """
    with open(config_file, encoding="utf-8") as fd:
        config = json.load(fd)
        return config["bpks"], config["ecos"]


def get_ecos_df(config: Dict[str, Any]) -> pd.DataFrame:
    """Scrape all ecos devices for trainswitches.

    Args:
        config (Dict[str, Any]): ecos config with port and ips

    Returns:
        pd.DataFrame: result
    """
    port = config["port"]
    df_dicts = []
    for ip in list(config["bpk_ip"].values())[1:]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as skt:
            skt.settimeout(0.5)
            skt.connect((ip, port))

            # hardcoded in api: ausgeben kompletter liste schaltartikel
            skt.sendall(b"queryObjects(11)" + b"\n")

            buffer = b""

            while b"<END 0 (OK)>" not in buffer:
                buffer += skt.recv(1024)

            data = skt.recv(1024).decode("utf-8")
            ecos_ids = data.split("\r\n")[1:-2]

            for ecos_id in ecos_ids:
                skt.sendall(f"get({ecos_id})".encode() + b"\n")
                data = skt.recv(10_000).decode("utf-8")
                switch_device = data.split("\r\n")[1:-2]

                d = {}
                for feature in switch_device:
                    _, _, desc = feature.partition(" ")
                    name, val = desc.split("[")
                    val = val[:-1]
                    d[name] = val
                d["id"] = ecos_id
                df_dicts.append(d)

    df = pd.DataFrame(df_dicts)
    df = df.loc[df.protocol == "DCC"]
    df = df.loc[df.name1.isin(list(config["bpk_ip"].keys()))]

    # TO DO insert guid col

    return df
