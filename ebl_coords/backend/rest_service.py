"""Initial setup for the API to attach observers from another deviec."""
from pickle import load as pickle_load
from queue import Queue
from typing import Dict

from fastapi import FastAPI, Request

from ebl_coords.backend.command.command import Command
from ebl_coords.backend.observable.gtcommand_subject import GtCommandSubject


class RestApi:
    """RestApi."""

    def __init__(
        self,
        worker_queue: Queue[Command],
        gtcommand_subject: GtCommandSubject,
    ) -> None:
        """Initialize the Api.

        Args:
            worker_queue (Queue[Command]): worker queue for commands
            gtcommand_subject (GtCommandSubject): gtcommand_subject
        """
        self.worker_queue = worker_queue
        self.gtcommand_subject = gtcommand_subject
        self.app = FastAPI()

        self._add_routes()

    def _add_routes(self) -> None:
        self.app.post("/gtcommand/all_coord")(self.all_coord)
        self.app.post("/gtcommand/changed_coord")(self.changed_coord)
        self.app.post("/gtcommand/ts_hit")(self.ts_hit)

    async def all_coord(self, observer: Request) -> Dict[str, str]:
        """Attach the observer sent to gtcommand_subject all_coords.

        Args:
            observer (Request): pickled observer to attach

        Returns:
            Dict[str, str]: json that will eventually contain the ip of the websocket
        """
        obs = pickle_load(observer.body)
        # Challenge: open a websocket and then make the received observer
        # register commands with the target being the websocket
        self.gtcommand_subject.attach_all_coord(obs)
        return {"message": "Hello World"}

    async def changed_coord(self, observer: Request) -> Dict[str, str]:
        """Attach the observer sent to gtcommand_subject changed_coord.

        Args:
            observer (Request): pickled observer to attach

        Returns:
            Dict[str, str]: json that will eventually contain the ip of the websocket
        """
        obs = pickle_load(observer.body)
        self.gtcommand_subject.attach_changed_coord(obs)
        return {"message": "Hello World"}

    async def ts_hit(self, observer: Request) -> Dict[str, str]:
        """Attach the observer sent to gtcommand_subject ts_hit.

        Args:
            observer (Request): pickled observer to attach

        Returns:
            Dict[str, str]: json that will eventually contain the ip of the websocket
        """
        obs = pickle_load(observer.body)
        self.gtcommand_subject.attach_ts_hit(obs)
        return {"message": "Hello World"}
