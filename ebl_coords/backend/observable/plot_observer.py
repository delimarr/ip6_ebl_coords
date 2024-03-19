"""Plotting Command and Observer."""
from queue import Queue

import numpy as np
import pyvista as pv

from ebl_coords.backend.command.base import Command
from ebl_coords.backend.observable.observer import Observer


class PlotCommand(Command):
    """Command to add a point to the pyvista plot.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: np.ndarray, context: pv.Plotter) -> None:
        """Initialize command with a new coordinate and the plotter.

        Args:
            content (np.ndarray): coordinates with dtype np.float32
            context (pv.Plotter): plotter
        """
        super().__init__(content, context)
        self.content: np.ndarray
        self.context: pv.Plotter

    def run(self) -> None:
        """Add the point to the plot."""
        self.context.add_points(self.content)


class PlotObserver(Observer):
    """Plot all coordinates from hook.

    Args:
        Observer (_type_): interface
    """

    def __init__(self, pl: pv.Plotter, command_queue: Queue[Command]) -> None:
        """Initialize with plot and command queue.

        Args:
            pl (pv.Plotter): plotter
            command_queue (_type_): command queue from invoker
        """
        self.pl = pl
        self.command_queue = command_queue

    def update(self) -> None:
        """Add the command."""
        self.command_queue.put(PlotCommand(self.result[1], self.pl))
