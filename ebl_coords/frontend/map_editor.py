"""Map Editor."""
from __future__ import annotations

import json
from dataclasses import asdict
from os import remove
from os.path import exists
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QListWidgetItem, QPushButton

from ebl_coords.backend.command.command import WrapperCommand, WrapperFunctionCommand
from ebl_coords.backend.command.db_cmd import MapDrawConnectTopoGuiCmd, MapDrawConnectTsGuiCmd
from ebl_coords.backend.command.db_cmd import MapFillCbGuiCmd, MapFillListGuiCmd
from ebl_coords.backend.constants import BLOCK_SIZE, ZONE_FILE
from ebl_coords.backend.observable.ecos_oberver import AttachEcosObsCommand
from ebl_coords.backend.observable.position_observer import AttachPositionCommand
from ebl_coords.backend.observable.ts_hit_observer import AttachTsHitObsCommand
from ebl_coords.decorators import override
from ebl_coords.frontend.command.map.redraw_cmd import RedrawCmd
from ebl_coords.frontend.custom_widgets import ClickableLabel, CustomZoneContainer
from ebl_coords.frontend.editor import Editor
from ebl_coords.frontend.map_data_elements.map_train_switch_dc import MapTsTopopoint
from ebl_coords.frontend.map_data_elements.zone_dc import Zone
from ebl_coords.frontend.net_maker import NetMaker
from ebl_coords.graph_db.data_elements.edge_relation_enum import EDGE_RELATION_TO_ENUM

if TYPE_CHECKING:
    from ebl_coords.frontend.gui import Gui


class MapEditor(Editor):
    """The Map editor."""

    def __init__(self, gui: Gui) -> None:
        """Build zone and create clickable label.

        Args:
            gui (Gui): gui
        """
        super().__init__(gui)
        self.selected_ts: MapTsTopopoint | None = None

        self._connect_ui_elements()

        self.zone: Zone = Zone(
            name="my_zone",
            block_size=BLOCK_SIZE,
            width=self.ui.map_zone_width.value(),
            height=self.ui.map_zone_height.value(),
            switches={},
        )
        self.net_maker: NetMaker = NetMaker(self.map_label, block_size=self.zone.block_size)
        self.fill_list()
        if exists(ZONE_FILE):
            self.load_json()
        self.fill_combobox()
        self.resize_map_label()

    def _connect_ui_elements(self) -> None:
        """Make map label and connect events."""
        self.map_label = ClickableLabel()
        self.map_label.setObjectName("map_label")
        self.map_label.clicked.connect(self.click_map)
        self.ui.map_right.layout().addWidget(self.map_label)

        self.ui.map_zone_speichern_btn.released.connect(self.save)
        self.ui.map_zone_neu_btn.released.connect(self.new_map_label)
        self.ui.map_zone_resize_btn.released.connect(self.resize_map_label)
        self.ui.map_position_CBox.currentIndexChanged.connect(self.map_pos_changed)
        self.ui.map_distance_dsb.valueChanged.connect(self.map_pos_changed)

    def register_observers(self) -> None:
        """Make and attach observers."""
        self.worker_queue.put(
            AttachTsHitObsCommand(
                content=(
                    self.gui.ebl_coords,
                    self.ui.map_position_CBox,
                )
            )
        )
        self.worker_queue.put(
            AttachEcosObsCommand(
                content=(self.gui_queue, self.worker_queue, self),
                context=self.gui.ebl_coords.ecos,
            )
        )
        self.worker_queue.put(AttachPositionCommand(content=self))

    def map_pos_changed(self) -> None:
        """Invoke update of gtcommand subject on QCombobox change."""
        self.worker_queue.put(RedrawCmd(content=(self, self.gui_queue), context=self.worker_queue))

    def load_json(self) -> None:
        """Create scene from a json file."""
        old_switches = self.zone.switches
        with open(ZONE_FILE, encoding="utf-8") as fd:
            zone_dict = json.load(fd)
            map_ts_dict = zone_dict["switches"]
            zone_dict["switches"] = {}
            self.zone = Zone(**zone_dict)
            for key, val in map_ts_dict.items():
                self.zone.switches[key] = MapTsTopopoint(**val)
        for key, val in old_switches.items():
            if not key in self.zone.switches.keys():
                self.zone.switches[key] = val
        self.net_maker = NetMaker(self.map_label, self.zone.block_size)
        self.ui.map_zone_width.setValue(self.zone.width)
        self.ui.map_zone_height.setValue(self.zone.height)

    def add_btns_to_list(self, text: str, guid_0: str, guid_1: str) -> None:
        """Create, add, connect custom buttons and add to zone.switches if new.

        Args:
            text (str): display text of button
            guid_0 (str): trainswitch guid_0
            guid_1 (str): trainswitch guid_1
        """
        item = QListWidgetItem(self.ui.map_weichen_list)
        zone_container = CustomZoneContainer(text, guid_0, guid_1)
        zone_container.neutral_btn.released.connect(
            lambda: self.select_ts(guid_0, zone_container.neutral_btn)
        )
        zone_container.deflection_btn.released.connect(
            lambda: self.select_ts(guid_1, zone_container.deflection_btn)
        )
        zone_container.straight_btn.released.connect(
            lambda: self.select_ts(guid_1, zone_container.straight_btn)
        )
        neutral_switch = MapTsTopopoint(
            name=text,
            guid=guid_0,
            relation=EDGE_RELATION_TO_ENUM[zone_container.neutral_btn.text()].name,
        )
        deflection_switch = MapTsTopopoint(
            name=f"{text}_1",
            guid=guid_1,
            relation=EDGE_RELATION_TO_ENUM[zone_container.deflection_btn.text()].name,
        )
        straight_switch = MapTsTopopoint(
            name=f"{text}_0",
            guid=guid_1,
            relation=EDGE_RELATION_TO_ENUM[zone_container.straight_btn.text()].name,
        )
        self.zone.switches.setdefault(
            f"{neutral_switch.guid}{neutral_switch.relation}", neutral_switch
        )
        self.zone.switches.setdefault(
            f"{deflection_switch.guid}{deflection_switch.relation}", deflection_switch
        )
        self.zone.switches.setdefault(
            f"{straight_switch.guid}{straight_switch.relation}", straight_switch
        )

        item.setSizeHint(zone_container.sizeHint())
        self.ui.map_weichen_list.setItemWidget(item, zone_container)

    def fill_list(self) -> None:
        """Clear and fill list with trainswitch buttons."""
        self.ui.map_weichen_list.clear()
        self.worker_queue.put(MapFillListGuiCmd(content=self, context=self.gui_queue))

    def fill_combobox(self) -> None:
        """Clear and fill position combobox."""
        self.ui.map_position_CBox.clear()
        self.worker_queue.put(
            MapFillCbGuiCmd(content=self.ui.map_position_CBox, context=self.gui_queue)
        )

    @override
    def reset(self) -> None:
        """Clear the form and reset the zone and zonemaker."""
        self.ui.map_weichen_list.clear()
        self.ui.map_zone_width.clear()
        self.ui.map_zone_height.clear()
        self.map_label.clear()
        self.fill_list()

    @override
    def save(self) -> None:
        """Save the zone as json."""
        with open(ZONE_FILE, "w", encoding="utf-8") as fd:
            json.dump(asdict(self.zone), fd, indent=4)

    def resize_map_label(self) -> None:
        """Resize the map_label."""
        width = self.ui.map_zone_width.text()
        height = self.ui.map_zone_height.text()
        if width and height:
            self.zone.width = int(width)
            self.zone.height = int(height)
        self.net_maker.resize_label(self.zone.width, self.zone.height)
        self.draw()

    def new_map_label(self) -> None:
        """Reset zone and reset net_maker.pixmap."""
        if exists(ZONE_FILE):
            remove(ZONE_FILE)
        self.zone = Zone(
            name="my_zone",
            block_size=BLOCK_SIZE,
            width=self.ui.map_zone_width.value(),
            height=self.ui.map_zone_height.value(),
            switches={},
        )
        self.fill_list()
        self.resize_map_label()

    def select_ts(self, guid: str, btn: QPushButton) -> None:
        """Select a train switch with its direction.

        Args:
            guid (str): node_idRelation
            btn (QPushButton): btn pressed
        """
        self.selected_ts = self.zone.switches[f"{guid}{EDGE_RELATION_TO_ENUM[btn.text()].name}"]

    def _draw_connect_topo(self) -> None:
        switches = list(self.zone.switches.values())
        for i in range(0, len(self.zone.switches), 3):
            neutral = switches[i]
            if neutral.coords is None:
                continue
            n1 = switches[i + 1]
            n2 = switches[i + 2]

            self.worker_queue.put(
                MapDrawConnectTopoGuiCmd(
                    content=(self.gui.ebl_coords, neutral, n1, self.net_maker),
                    context=self.gui_queue,
                )
            )
            self.worker_queue.put(
                MapDrawConnectTopoGuiCmd(
                    content=(self.gui.ebl_coords, neutral, n2, self.net_maker),
                    context=self.gui_queue,
                )
            )

    def draw(self) -> None:
        """Draw the net."""
        # draw colored line, based on train position. Use ecos lookup tabel and self.ts_hit_observer.result (current ts)
        self.net_maker.draw_grid(self.zone.width, self.zone.height)

        # draw topo points
        for ts in self.zone.switches.values():
            if ts.coords is not None:
                u, v = ts.coords
                self.net_maker.draw_grid_point(u, v)
                self.net_maker.draw_grid_text(ts.name, u, v)

        self._draw_connect_topo()
        self.worker_queue.put(
            MapDrawConnectTsGuiCmd(
                content=(self.zone.switches, self.net_maker), context=self.gui_queue
            )
        )
        self.worker_queue.put(
            WrapperCommand(
                content=WrapperFunctionCommand(content=self.net_maker.show), context=self.gui_queue
            )
        )

    def click_map(self) -> None:
        """Set a topo point on the map and redraw."""
        if self.selected_ts is not None:
            position = self.map_label.click_event.position()
            coords = self.net_maker.get_grid_coords(position.x(), position.y())
            self.selected_ts.coords = (int(coords[0]), int(coords[1]))
            self.selected_ts = None
            self.net_maker.clear()
            self.draw()
