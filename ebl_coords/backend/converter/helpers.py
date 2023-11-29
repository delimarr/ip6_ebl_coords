"""Helper functions for converters."""
import json
import time
from typing import Any, List

import numpy as np
import pandas as pd

from ebl_coords.backend.converter.converter_output import ConverterOuput


def df_to_converter_output(
    df: pd.DataFrame,
    time_stamp_key: str = "time_after_start_ms",
) -> List[ConverterOuput]:
    """Transform DataFrame to List of Converter Ouput objects.

    Args:
        df (pd.DataFrame): DataFrame containing at least x, y, z and a timestamp column.
        time_stamp_key (str, optional): index name of timestamp. Defaults to "time_after_start_ms".

    Returns:
        List[ConverterOuput]: list of Converter Output objects.
    """
    res = []
    non_misc_keys = np.array(["x", "y", "z", time_stamp_key])
    for i in range(df.shape[0]):
        row = df.loc[i, non_misc_keys]
        misc = df.loc[i, df.columns.difference(non_misc_keys)]
        row_dc = ConverterOuput(
            x=row.x,
            y=row.y,
            z=row.z,
            time_stamp=row[time_stamp_key],
            misc=misc.to_dict(),
        )
        res.append(row_dc)
    return res


class NpEncoder(json.JSONEncoder):
    """Encode numpy datatypes to python native.

    Args:
        json (_type_): json encoder
    """

    def default(self, o: object) -> Any:
        """Convert numpy objects to python native ones.

        Args:
            o (object):

        Returns:
            o: python native primtive or object.
        """
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


def now_ms() -> int:
    """Get unix timestamp.

    Returns:
        int: ms
    """
    return int(time.time() * 1000)
