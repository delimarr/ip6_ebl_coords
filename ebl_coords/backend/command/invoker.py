"""An command invoker class."""
from __future__ import annotations

import time
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ebl_coords.backend.command.command import Command


class Invoker:
    """A command invoker."""

    def start_loop(self, queue: Queue[Command], interval_s: float) -> Thread:
        """Run all commands in a new thread from queue every interval_s.

        Args:
            queue (Queue[Command]): command queue
            interval_s (float): time delta in seconds
        """

        def _timer_loop() -> None:
            while True:
                while not queue.empty():
                    cmd = queue.get()
                    cmd.run()
                time.sleep(interval_s)

        thread = Thread(target=_timer_loop, daemon=True)
        thread.start()
        return thread
