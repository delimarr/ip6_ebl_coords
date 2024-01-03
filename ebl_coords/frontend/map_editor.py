"""Map Editor."""
from typing import Optional

from PyQt6.QtWidgets import QListWidgetItem, QPushButton

from ebl_coords.decorators import override
from ebl_coords.frontend.custom_widgets import ClickableLabel, CustomZoneContainer
from ebl_coords.frontend.editor import Editor
from ebl_coords.frontend.main_gui import Ui_MainWindow
from ebl_coords.frontend.map_data_elements.map_train_switch_dc import MapTrainSwitch
from ebl_coords.frontend.map_data_elements.zone_dc import Zone
from ebl_coords.frontend.zone_maker import ZoneMaker
from ebl_coords.graph_db.api import Api
from ebl_coords.graph_db.data_elements.edge_relation_enum import EDGE_RELATION_TO_ENUM
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation


class MapEditor(Editor):
    """The Map editor."""

    def __init__(self, ui: Ui_MainWindow, graph_db: Api) -> None:
        """Initialize the editor with a window and a graph_db api.

        Args:
            ui (Ui_MainWindow): main window
            graph_db (Api): graph db api
        """
        super().__init__(ui, graph_db)
        self.selected_ts: Optional[MapTrainSwitch] = None

        self.map_label = ClickableLabel()
        self.map_label.setObjectName("map_label")
        self.map_label.clicked.connect(self.click_map)
        self.ui.map_right.layout().addWidget(self.map_label)

        self.ui.map_zone_speichern_btn.released.connect(self.save)

        self.zone: Zone
        self.zone_maker: ZoneMaker
        self.reset()

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
        neutral_switch = MapTrainSwitch(
            guid=guid_0,
            relation=EDGE_RELATION_TO_ENUM[zone_container.neutral_btn.text()].name,
        )
        deflection_switch = MapTrainSwitch(
            guid=guid_1,
            relation=EDGE_RELATION_TO_ENUM[zone_container.deflection_btn.text()].name,
        )
        straight_switch = MapTrainSwitch(
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

    def _fill_list(self) -> None:
        cmd = "MATCH (node:WEICHE) RETURN node.bhf, node.name, node.node_id"
        df = self.graph_db.run_query(cmd)[::2]
        for _, row in df.iterrows():
            guid = row["node.node_id"]
            self._add_btns_to_list(
                text=f"{row['node.bhf']}_{row['node.name']}",
                guid_0=guid,
                guid_1=guid[:-1] + "1",
            )

    @override
    def reset(self) -> None:
        """Clear the form and reset the zone and zonemaker."""
        self.ui.map_weichen_list.clear()
        self.selected_ts = None
        self.ui.map_zonename_txt.clear()
        self.ui.map_zone_width.clear()
        self.ui.map_zone_height.clear()
        self.zone = Zone(name="", block_size=41, width=0, height=0, switches={})
        self.zone_maker = ZoneMaker(self.map_label, block_size=self.zone.block_size)
        self._fill_list()

    @override
    def save(self) -> None:
        """Draw the zone."""
        self.zone.name = self.ui.map_zonename_txt.text()
        self.zone.width = int(self.ui.map_zone_width.text())
        self.zone.height = int(self.ui.map_zone_height.text())
        self._draw()
        # to do write to file

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
            if n1.coords is not None:
                ut, vt = n1.coords
                self.zone_maker.draw_grid_line(u, v, ut, vt)
            if n2.coords is not None:
                ut, vt = n2.coords
                self.zone_maker.draw_grid_line(u, v, ut, vt)

    def _draw_connect_ts(self) -> None:
        for relation in EdgeRelation:
            if relation == EdgeRelation.DOUBLE_VERTEX:
                continue
            cmd = f"MATCH (n1)-[e:{relation.name}]->(n2) RETURN n1.node_id, n2.node_id, e.target"
            df = self.graph_db.run_query(cmd)
            if df.size > 0:
                for _, row in df.iterrows():
                    if row["e.target"] is not None:
                        ts1 = self.zone.switches[f"{row['n1.node_id']}{relation.name}"]
                        ts2 = self.zone.switches[
                            f"{row['n2.node_id']}{row['e.target']}"
                        ]
                        if ts1.coords and ts2.coords:
                            u1, v1 = ts1.coords
                            u2, v2 = ts2.coords
                            self.zone_maker.draw_grid_line(u1, v1, u2, v2)

    def _draw(self) -> None:
        self.zone_maker.draw_grid(self.zone.width, self.zone.height)

        # draw topo points
        for ts in self.zone.switches.values():
            if ts.coords is not None:
                self.zone_maker.draw_grid_point(ts.coords[0], ts.coords[1])

        self._draw_connect_topo()
        self._draw_connect_ts()

    def click_map(self) -> None:
        """Set a topo point on the map and redraw."""
        if self.selected_ts is not None:
            position = self.map_label.click_event.position()
            coords = self.zone_maker.get_grid_coords(position.x(), position.y())
            self.selected_ts.coords = (int(coords[0]), int(coords[1]))
            self.selected_ts = None

            self._draw()
