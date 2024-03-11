"""Provide ecos scraper and config loader."""
import json
import socket
import warnings
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from ebl_coords.backend.constants import MOCK_FLG
from ebl_coords.graph_db.graph_db_api import GraphDbApi


def load_config(config_file: str) -> Tuple[List[str], Dict[str, Any]]:
    """Load ecos json config file.

    Args:
        config_file (str): path with filename

    Returns:
        Tuple[List[str], Dict[str, Any]]: bkps, ecos
    """
    with open(config_file, encoding="utf-8") as fd:
        config = json.load(fd)
        bpks: List[str] = config["bpks"]
        ecos_config: Dict[str, Any] = config["ecos"]
        if MOCK_FLG:
            for key in ecos_config["bpk_ip"].keys():
                ecos_config["bpk_ip"][key] = "127.0.0.1"
                ecos_config["port"] = 42043
        return bpks, ecos_config


def get_ecos_df(config: Dict[str, Any], bpks: List[str]) -> pd.DataFrame:
    """Scrape all ecos devices for trainswitches.

    Args:
        config (Dict[str, Any]): ecos config with port and ips

    Returns:
        pd.DataFrame: result
    """
    if MOCK_FLG:
        warnings.warn("used ecos mock, only use DAB.")
        df = _get_ecos_df_mock(config, bpks)
    df = _get_ecos_df_live(config, bpks)
    df.id = df.id.astype(int)
    return df


def _select_valid_bpks(df: pd.DataFrame, bpks: List[str]) -> pd.DataFrame:
    df = df.loc[df.protocol == "DCC"]
    return df.loc[df.name1.isin(bpks)]


def _add_db_guid(df: pd.DataFrame) -> pd.DataFrame:
    cmd = "MATCH (n) RETURN n.node_id AS node_id, n.ecos_id AS dcc, n.bhf AS bpk"
    db = GraphDbApi().run_query(cmd)[::2]
    db.bpk = '"' + db.bpk + '"'
    df.insert(df.shape[1], column="guid", value=np.nan)
    df.guid = df.guid.astype(object)
    for _, row in db.iterrows():
        dcc = int(row.dcc)
        idx = df.guid.loc[
            (df["name1"] == row.bpk) & (df["addr"].astype(int) == dcc)
        ].index
        df.loc[idx, "guid"] = row.node_id
    return df.dropna()


def _get_ecos_df_mock(config: Dict[str, Any], bpks: List[str]) -> pd.DataFrame:
    df = pd.read_csv("./ecos_mock/ecos.csv")
    df = df.loc[df.protocol == "DCC"]
    df = df.loc[df.name1.isin(bpks)]
    df.insert(df.shape[1], column="ip", value=config["bpk_ip"]["DAB"])
    df = _add_db_guid(df)
    return df


def _get_ecos_df_live(config: Dict[str, Any], bpks: List[str]) -> pd.DataFrame:
    port = config["port"]
    df_dicts = []
    for ip in list(config["bpk_ip"].values())[1:]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as skt:
            skt.connect((ip, port))

            # hardcoded in api: ausgeben kompletter Liste Schaltartikel
            skt.sendall(b"queryObjects(11)" + b"\n")

            buffer = b""

            # check delimiter
            while b"<END 0 (OK)>" not in buffer:
                buffer += skt.recv(1024)

            data = buffer.decode("utf-8")
            ecos_ids = data.split("\r\n")[1:-2]

            for ecos_id in ecos_ids:
                skt.sendall(f"get({ecos_id})".encode() + b"\n")
                # TO DO clean up 10_000 recv
                data = skt.recv(10_000).decode("utf-8")
                switch_device = data.split("\r\n")[1:-2]

                d = {}
                for feature in switch_device:
                    _, _, desc = feature.partition(" ")
                    name, val = desc.split("[")
                    val = val[:-1]
                    d[name] = val
                d["id"] = ecos_id
                d["ip"] = ip
                df_dicts.append(d)

    df = pd.DataFrame(df_dicts)
    df = _select_valid_bpks(df, bpks)
    df = _add_db_guid(df)
    return df
