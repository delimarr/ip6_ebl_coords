"""Observer in order to receive ecos updates."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ebl_coords.backend.command.command import Command
from ebl_coords.backend.command.ecos_cmd import UpdateStateCommand
from ebl_coords.backend.observable.observer import Observer
from ebl_coords.decorators import override
from ebl_coords.frontend.command.map.redraw_cmd import RedrawCmd

if TYPE_CHECKING:
    from queue import Queue

    from ebl_coords.backend.observable.ecos_subject import EcosSubject
    from ebl_coords.frontend.map_editor import MapEditor


class EcosObserver(Observer):
    """Obersver pattern for ecos.

    Args:
        Observer (_type_): interface
    """

    def __init__(
        self,
        gui_queue: Queue[Command],
        worker_queue: Queue[Command],
        map_editor: MapEditor,
    ) -> None:
        """Initialize ecos observer.

        Args:
            gui_queue (Queue[Command]): gui_queue
            worker_queue (Queue[Command]): worker_queue
            map_editor (MapEditor): map editor
        """
        self.gui_queue = gui_queue
        self.worker_queue = worker_queue
        self.map_editor = map_editor

    @override
    def update(self) -> None:
        """Put update and redraw command in queue."""
        self.worker_queue.put(
            UpdateStateCommand(content=self.result, context=self.map_editor.gui.ebl_coords.ecos_df)
        )

        self.worker_queue.put(
            RedrawCmd(content=(self.map_editor, self.gui_queue), context=self.worker_queue)
        )


class AttachEcosObsCommand(Command):
    """Create and attach an EcosObserver.

    Args:
        Command (_type_): interface
    """

    def __init__(
        self,
        content: tuple[Queue[Command], Queue[Command], MapEditor],
        context: EcosSubject,
    ) -> None:
        """Initialize this command.

        Args:
            content (Tuple[Queue[Command], Queue[Command], MapEditor]): (gui_queue, worker_queue, map_editor)
            context (EcosSubject): EcosSubject
        """
        super().__init__(content, context)
        self.content: tuple[Queue[Command], Queue[Command], MapEditor]
        self.context: EcosSubject

    @override
    def run(self) -> None:
        """Create and attach an EcosObserver."""
        gui_queue, worker_queue, map_editor = self.content
        self.context.attach(
            EcosObserver(gui_queue=gui_queue, worker_queue=worker_queue, map_editor=map_editor)
        )
