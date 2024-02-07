"""Map Editor."""
from __future__ import annotations

import json
from dataclasses import asdict
from os.path import exists
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QListWidgetItem, QPushButton

from ebl_coords.backend.command.gui_cmd import DrawOccupiedNetCommand
from ebl_coords.backend.constants import BLOCK_SIZE, ZONE_FILE
from ebl_coords.backend.observable.ecos_oberver import EcosObserver
from ebl_coords.backend.observable.ts_hit_observer import TsHitObserver
from ebl_coords.decorators import override
from ebl_coords.frontend.custom_widgets import ClickableLabel, CustomZoneContainer
from ebl_coords.frontend.editor import Editor
from ebl_coords.frontend.map_data_elements.map_train_switch_dc import MapTsTopopoint
from ebl_coords.frontend.map_data_elements.zone_dc import Zone
from ebl_coords.frontend.net_maker import NetMaker
from ebl_coords.graph_db.data_elements.edge_relation_enum import EDGE_RELATION_TO_ENUM
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem

if TYPE_CHECKING:
    from ebl_coords.main import MainWindow


class MapEditor(Editor):
    """The Map editor."""

    def __init__(self, main_window: MainWindow) -> None:
        """Build zone and create clickable label.

        Args:
            main_window (MainWindow): main_window
        """
        super().__init__(main_window)
        self.ts_hit_observer: TsHitObserver
        self.ecos_oberver: EcosObserver

        self.selected_ts: MapTsTopopoint | None = None

        self._connect_ui_elements()

        self.zone: Zone = Zone(
            name="my_zone",
            block_size=BLOCK_SIZE,
            width=self.ui.map_zone_width.value(),
            height=self.ui.map_zone_height.value(),
            switches={},
        )
        self.net_maker: NetMaker = NetMaker(
            self.map_label, block_size=self.zone.block_size
        )
        self.fill_list()
        self.fill_combobox()
        if exists(ZONE_FILE):
            self.load_json()

    def _connect_ui_elements(self) -> None:
        """Make map label and connect events."""
        self.map_label = ClickableLabel()
        self.map_label.setObjectName("map_label")
        self.map_label.clicked.connect(self.click_map)
        self.ui.map_right.layout().addWidget(self.map_label)

        self.ui.map_zone_speichern_btn.released.connect(self.save)
        self.ui.map_zone_neu_btn.released.connect(self.reset)
        self.ui.map_position_CBox.currentIndexChanged.connect(self._map_pos_changed)

    def register_observers(self) -> None:
        """Make and attach observers."""
        command_queue = self.main_window.command_queue
        self.ts_hit_observer = TsHitObserver(self.main_window)
        self.gtcommand.attach(self.ts_hit_observer)
        self.ecos_oberver = EcosObserver(
            command_queue=command_queue, ecos_df=self.main_window.ecos_df
        )
        self.main_window.ecos.attach(self.ecos_oberver)

    def _map_pos_changed(self) -> None:
        """Invoke update of gtcommand subject on QCombobox change."""
        edge_id = self.ui.map_position_CBox.currentData()
        if edge_id:
            self.main_window.gtcommand.set_next_ts(edge_id=edge_id)

            weiche = SwitchItem.WEICHE.name
            cmd = f"""
            MATCH(n1:{weiche})-[r]->(n2:{weiche})
            WHERE r.edge_id = '{edge_id}'
            RETURN r.edge_id AS edge_id, type(r) AS ts_source, r.target AS ts_dest, n1.node_id AS source_id, n2.node_id as dest_id
            """
            df = self.graph_db.run_query(cmd)
            assert df.shape[0] == 1

            self.main_window.command_queue.put(
                DrawOccupiedNetCommand(content=df, context=self)
            )

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
        self.draw()

    def _add_btns_to_list(self, text: str, guid_0: str, guid_1: str) -> None:
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
        self.zone.switches[
            f"{neutral_switch.guid}{neutral_switch.relation}"
        ] = neutral_switch
        self.zone.switches[
            f"{deflection_switch.guid}{deflection_switch.relation}"
        ] = deflection_switch
        self.zone.switches[
            f"{straight_switch.guid}{straight_switch.relation}"
        ] = straight_switch

        item.setSizeHint(zone_container.sizeHint())
        self.ui.map_weichen_list.setItemWidget(item, zone_container)

    def fill_list(self) -> None:
        """Clear and fill list with trainswitch buttons."""
        self.ui.map_weichen_list.clear()
        cmd = "MATCH (node:WEICHE) RETURN node.bhf, node.name, node.node_id"
        df = self.graph_db.run_query(cmd)[::2]
        df.sort_values(by=["node.bhf", "node.name"], inplace=True)
        for _, row in df.iterrows():
            guid = row["node.node_id"]
            name = f"{row['node.bhf']}_{row['node.name']}"
            self._add_btns_to_list(
                text=name,
                guid_0=guid,
                guid_1=guid[:-1] + "1",
            )

    def fill_combobox(self) -> None:
        """Clear and fill position combobox."""
        self.ui.map_position_CBox.clear()
        for guid, name in self.graph_db.edges_tostring():
            self.ui.map_position_CBox.addItem(name, guid)

    @override
    def reset(self) -> None:
        """Clear the form and reset the zone and zonemaker."""
        self.ui.map_weichen_list.clear()
        self.selected_ts = None
        self.ui.map_zone_width.clear()
        self.ui.map_zone_height.clear()
        self.map_label.clear()
        self.fill_list()

    @override
    def save(self) -> None:
        """Draw the zone and export to json."""
        width = self.ui.map_zone_width.text()
        height = self.ui.map_zone_height.text()
        if width and height:
            self.zone.width = int(width)
            self.zone.height = int(height)
            # write to file
            with open(ZONE_FILE, "w", encoding="utf-8") as fd:
                json.dump(asdict(self.zone), fd, indent=4)
            self.draw()

    def select_ts(self, guid: str, btn: QPushButton) -> None:
        """Select a train switch with its direction.

        Args:
            guid (str): node_idRelation
            btn (QPushButton): btn pressed
        """
        self.selected_ts = self.zone.switches[
            f"{guid}{EDGE_RELATION_TO_ENUM[btn.text()].name}"
        ]

    def _draw_connect_topo(self) -> None:
        switches = list(self.zone.switches.values())
        for i in range(0, len(self.zone.switches), 3):
            neutral = switches[i]
            n1 = switches[i + 1]
            n2 = switches[i + 2]
            if neutral.coords is None:
                continue

            u, v = neutral.coords
            state = self.main_window.ecos_df.loc[
                self.main_window.ecos_df.guid == neutral.guid
            ].state.iloc[0]

            if n1.coords is not None:
                ut, vt = n1.coords
                snap_to_border = (
                    n1.relation == EdgeRelation.STRAIGHT.name
                    and state == 1
                    or n1.relation == EdgeRelation.DEFLECTION.name
                    and state == 0
                )
                self.net_maker.draw_grid_line(u, v, ut, vt, snap_first=snap_to_border)
            if n2.coords is not None:
                ut, vt = n2.coords
                snap_to_border = (
                    n2.relation == EdgeRelation.STRAIGHT.name
                    and state == 1
                    or n2.relation == EdgeRelation.DEFLECTION.name
                    and state == 0
                )
                self.net_maker.draw_grid_line(u, v, ut, vt, snap_first=snap_to_border)

    def _draw_connect_ts(self) -> None:
        double_vertex = EdgeRelation.DOUBLE_VERTEX.name
        cmd = f"""
        MATCH (n1)-[r]->(n2)\
        WHERE NOT type(r) = '{double_vertex}'\
        RETURN n1.node_id, n2.node_id, r.target AS target, type(r) AS relation
        """
        df = self.graph_db.run_query(cmd)
        if df.size > 0:
            for _, row in df.iterrows():
                if row["target"] is not None:
                    ts1 = self.zone.switches[f"{row['n1.node_id']}{row['relation']}"]
                    ts2 = self.zone.switches[f"{row['n2.node_id']}{row['target']}"]
                    if ts1.coords and ts2.coords:
                        u1, v1 = ts1.coords
                        u2, v2 = ts2.coords
                        self.net_maker.draw_grid_line(u1, v1, u2, v2, snap_first=False)

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
        self._draw_connect_ts()

    def click_map(self) -> None:
        """Set a topo point on the map and redraw."""
        if self.selected_ts is not None:
            position = self.map_label.click_event.position()
            coords = self.net_maker.get_grid_coords(position.x(), position.y())
            self.selected_ts.coords = (int(coords[0]), int(coords[1]))
            self.selected_ts = None
            self.draw()
