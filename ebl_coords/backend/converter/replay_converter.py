"""Read from file and stream to socket."""

from typing import List

from ebl_coords.backend.converter.base_converter import BaseConverter
from ebl_coords.backend.converter.converter_output import ConverterOuput
from ebl_coords.backend.converter.helpers import now_ms
from ebl_coords.backend.transform_data import get_df


class ReplayConverter(BaseConverter):
    """Replay a file."""

    def __init__(
        self,
        folder: str,
        files: List[str],
        raw_flg: bool = False,
        ip_server: str = "127.0.0.1",
        port_server: int = 42042,
    ) -> None:
        """Initialize with given files in folder.

        Args:
            folder (str): full path to parent folder containing all files.
            files (List[str]): files to concat
            raw_flg (bool, optional): Set to true if raw got outputfiles are used. Defaults to False.
            ip_server (str, optional): ip adress. Defaults to "127.0.0.1".
            port_server (int, optional): port. Defaults to 42042.
        """
        super().__init__(ip_server, port_server)
        self.raw_flg = raw_flg
        self.df = get_df(files, folder)

    def read_input(self) -> None:
        """Fill self.buffer with entries from files. Line by line with respect to timestamps."""
        start_t = self.df.time_after_start_ms[0]
        delta_t = now_ms() - start_t

        for _, row in self.df.iterrows():
            while (now_ms() - delta_t) < row.time_after_start_ms:
                # wait
                pass
            misc_idx = row.index.difference(["x", "y", "z", "pc_timestamp"])
            if self.raw_flg:
                self.raw_buffer.put(
                    row.to_string(header=False, index=False)
                    .replace("\n", ",")
                    .replace(" ", "")
                    + ";"
                )
            else:
                self.buffer.put(
                    ConverterOuput(now_ms(), row.x, row.y, row.z, dict(row[misc_idx]))
                )
