"""Command pattern Graph Db."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import numpy as np
import pandas as pd

from ebl_coords.backend.command.command import Command
from ebl_coords.backend.constants import ECOS_DF_LOCK
from ebl_coords.backend.observable.gtcommand_subject import GtCommandSubject
from ebl_coords.decorators import override
from ebl_coords.frontend.command.combobox_cmd import AddComboBoxElementCmd, SetComboBoxCmd
from ebl_coords.frontend.command.combobox_cmd import SetComboBoxContentCmd
from ebl_coords.frontend.command.label_cmd import SetTextCmd
from ebl_coords.frontend.command.map.add_btns_to_list_cmd import MapAddCustomButtonsToListCmd
from ebl_coords.frontend.command.map.draw_cmd import DrawCmd
from ebl_coords.frontend.command.map.draw_grid_line_cmd import DrawGridLineCmd
from ebl_coords.frontend.command.map.draw_occupied_cmd import DrawOccupiedNetCmd
from ebl_coords.frontend.command.qlist_cmd import AddCustomButtonToListCmd
from ebl_coords.frontend.command.strecken.strecken_reset_cmd import StreckenResetCmd
from ebl_coords.graph_db.data_elements.bpk_enum import Bpk
from ebl_coords.graph_db.data_elements.edge_dc import Edge
from ebl_coords.graph_db.data_elements.edge_relation_enum import EDGE_RELATION_TO_ENUM, TRAINRAILS
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation
from ebl_coords.graph_db.data_elements.node_dc import Node
from ebl_coords.graph_db.data_elements.switch_item_enum import SwitchItem
from ebl_coords.graph_db.graph_db_api import GraphDbApi
from ebl_coords.graph_db.query_generator import generate_guid, get_double_nodes, single_edge

if TYPE_CHECKING:
    from queue import Queue

    from PyQt6.QtWidgets import QComboBox, QListWidget

    from ebl_coords.frontend.main_gui import Ui_MainWindow
    from ebl_coords.frontend.map_data_elements.map_train_switch_dc import MapTsTopopoint
    from ebl_coords.frontend.map_editor import MapEditor
    from ebl_coords.frontend.net_maker import NetMaker
    from ebl_coords.frontend.strecken_editor import StreckenEditor


def get_strecken_df() -> pd.DataFrame:
    """Get df containing all trainswitches from all strecken."""
    cmd = "MATCH (node:WEICHE) RETURN node.bhf AS bhf, node.name AS name, node.node_id AS node_id"
    strecken_df = GraphDbApi().run_query(cmd)[::2]
    shape = strecken_df.shape[0]
    strecken_df = pd.concat([strecken_df] * 3, ignore_index=True)
    exits = TRAINRAILS * shape
    exits.sort()
    strecken_df.insert(strecken_df.shape[1], "exit", exits)
    mask = strecken_df.exit != EdgeRelation.NEUTRAL.value
    strecken_df.loc[mask, "node_id"] = strecken_df[mask]["node_id"].apply(lambda x: x[:-1] + "1")
    strecken_df.sort_values(by=["bhf", "name"], inplace=True)
    return strecken_df


def get_node(bpk: str, ts_number: str, relation: str) -> Node:
    """Create a node from input.

    Args:
        bpk (str): betriebspunkt
        ts_number (str): trainswitch number
        relation (str): relation from ts

    Returns:
        Node: node
    """
    strecken_df = get_strecken_df()
    n = strecken_df.loc[
        (strecken_df["bhf"] == bpk)
        & (strecken_df["name"] == ts_number)
        & (strecken_df["exit"] == relation)
    ].iloc[0, :]
    return Node(
        id=n["node_id"],
        ecos_id="",
        switch_item=SwitchItem.WEICHE,
        ts_number=n["name"],
        bpk=Bpk[bpk],
        coords=np.zeros((3,)),
    )


class DbCommand(Command):
    """Command pattern.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: str) -> None:
        """Initialize command with query.

        Args:
            content (str): query call
        """
        super().__init__(content)
        self.context: GraphDbApi = GraphDbApi()

    @override
    def run(self) -> None:
        """Execute query."""
        self.context.run_query(self.content)


class OccupyNextEdgeGuiCommand(Command):
    """Get next edge to occupy.

    Args:
        Command (_type_): interface
    """

    def __init__(
        self, content: tuple[str, pd.DataFrame, QComboBox], context: Queue[Command]
    ) -> None:
        """Initialize occupy command.

        Args:
            content (tuple[str, pd.DataFrame, QComboBox]): (source node_id, ecos Dataframe, QComboBox)
            context (MapEditor): map editor
        """
        super().__init__(content, context)
        self.content: tuple[str, pd.DataFrame, QComboBox]
        self.context: Queue[Command]
        self.node_id, self.ecos_df, self.combo_box = self.content

    @override
    def run(self) -> None:
        """Get next edge and update QCombobox."""
        weiche = SwitchItem.WEICHE.name
        double_vertex = EdgeRelation.DOUBLE_VERTEX.name

        relation = EdgeRelation.NEUTRAL.name

        # check if deflection/ straight exit will be used.
        if self.node_id[-1] == "0":
            neutral_node_id = f"{self.node_id[:-1]}0"
            with ECOS_DF_LOCK:
                state = self.ecos_df.loc[self.ecos_df.guid == neutral_node_id].state.iloc[0]
            state = int(state)
            assert state in (0, 1)
            if state == 0:
                relation = EdgeRelation.STRAIGHT.name
            else:
                relation = EdgeRelation.DEFLECTION.name

        cmd = f"""
        MATCH(n1:{weiche}{{node_id:'{self.node_id}'}})-[dv:{double_vertex}]->(n2:{weiche})
        MATCH(n2)-[r:{relation}]->(t)
        RETURN r.edge_id AS edge_id
        """
        df = GraphDbApi().run_query(cmd)
        assert df.shape[0] <= 1
        if df.shape[0] == 1:
            next_edge_id = df.edge_id.iloc[0]

            self.context.put(SetComboBoxCmd(content=next_edge_id, context=self.combo_box))


class FillTsListGuiCommand(Command):
    """Fill a list with trainswitch buttons.

    Args:
        Command (_type_): interface
    """

    def __init__(
        self, content: tuple[QListWidget, Callable[..., Any]], context: Queue[Command]
    ) -> None:
        """Initialize this command.

        Args:
            content (tuple[QListWidget, Callable[..., Any]]): (QListWidget, foo: function to bind all button click)
            context (Queue[Command]): gui_queue
        """
        super().__init__(content, context)
        self.content: tuple[QListWidget, Callable[..., Any]]
        self.context: Queue[Command]

    @override
    def run(self) -> None:
        """Create multiple buttons, add them to list, connect them to foo."""
        query_call = (
            "MATCH (node:WEICHE) RETURN node.bhf AS bhf, node.name AS name, node.node_id AS guid"
        )
        df = GraphDbApi().run_query(query_call)[::2]
        df.sort_values(by=["bhf", "name"], inplace=True)
        qlist, foo = self.content
        for _, row in df.iterrows():
            self.context.put(
                AddCustomButtonToListCmd(
                    content={
                        "callable": foo,
                        "guid": row["guid"],
                        "text": f"{row['bhf']}_{row['name']}",
                    },
                    context=qlist,
                )
            )


class GetTsGuiCommand(Command):
    """Get a trainswitch from db and set all labels in gui.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: tuple[str, Ui_MainWindow], context: Queue[Command]) -> None:
        """Initialize this command.

        Args:
            content (tuple[str, Ui_MainWindow]): (guid, ui)
            context (Queue[Command]): gui_queue
        """
        super().__init__(content, context)
        self.context: Queue[Command]
        self.content: tuple[str, Ui_MainWindow]

    @override
    def run(self) -> None:
        """Get data for trainswitch and create gui_cmds."""
        guid, ui = self.content
        cmd = get_double_nodes(guid)
        df = GraphDbApi().run_query(cmd)

        self.context.put(SetTextCmd(df["n1.bhf"][0], ui.weichen_bhf_txt))
        self.context.put(SetTextCmd(df["n1.ecos_id"][0], ui.weichen_dcc_txt))
        self.context.put(SetTextCmd(df["n1.name"][0], ui.weichen_weichenname_txt))
        self.context.put(
            SetTextCmd(
                f"({df['n1.x'][0]}, {df['n1.y'][0]}, {df['n1.z'][0]})",
                ui.weichen_coord_label,
            )
        )


class FillStreckenCBGuiCommand(Command):
    """Fill combobox with edges.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: Ui_MainWindow, context: Queue[Command]) -> None:
        """Initialize this command.

        Args:
            content (Ui_MainWindow): ui
            context (Queue[Command]): gui_queue
        """
        super().__init__(content, context)
        self.content: Ui_MainWindow
        self.context: Queue[Command]

    @override
    def run(self) -> None:
        """Fill strecken combo box from db."""
        strecken_df = get_strecken_df()
        items = strecken_df["bhf"] + "\t" + strecken_df["name"] + "\t" + strecken_df["exit"]
        self.context.put(
            SetComboBoxContentCmd(content=items, context=self.content.strecken_comboBox_a)
        )
        self.context.put(
            SetComboBoxContentCmd(content=items, context=self.content.strecken_comboBox_b)
        )


class FillStreckenListGuiCommand(Command):
    """Fill strecken_list from db.

    Args:
        Command (_type_): interface
    """

    def __init__(
        self, content: tuple[QListWidget, Callable[..., Any]], context: Queue[Command]
    ) -> None:
        """Create and add Custom Buttons to QListWidget using commands.

        Args:
            content (Tuple[QListWidget, Callable[..., Any]]): QListWidget, same callback function for all Custom Buttons
            context (Queue[Command]): gui_queue
        """
        super().__init__(content, context)
        self.content: tuple[QListWidget, Callable[..., Any]]
        self.context: Queue[Command]

    @override
    def run(self) -> None:
        """Get all edges from db and fill the list."""
        qlist, foo = self.content
        for guid, edge in GraphDbApi().edges_tostring():
            self.context.put(
                AddCustomButtonToListCmd(
                    content={"callable": foo, "guid": guid, "text": edge}, context=qlist
                )
            )


class StreckenSaveGuiCmd(Command):
    """Save a new strecke in db and reset strecken_editor.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: tuple[StreckenEditor, str, str], context: Queue[Command]) -> None:
        """Save new edge in db.

        Args:
            content (Tuple[StreckenEditor, str, str]): (strecken_editor, QComboBox A text, QComboBox B text)
            context (Queue[Command]): gui_queue
        """
        super().__init__(content, context)
        self.content: tuple[StreckenEditor, str, str]
        self.context: Queue[Command]

    def run(self) -> None:
        """Get data of strecke and create gui_cmds."""
        bhf1, name1, relation1 = self.content[1].split("\t")
        bhf2, name2, relation2 = self.content[2].split("\t")
        n1 = get_node(bhf1, name1, relation1)
        n2 = get_node(bhf2, name2, relation2)
        guid = generate_guid()
        edge1 = Edge(
            id=f"{guid}_0",
            source=n1,
            dest=n2,
            relation=EDGE_RELATION_TO_ENUM[relation1],
            target=EDGE_RELATION_TO_ENUM[relation2],
            distance=0,
        )
        edge2 = Edge(
            id=f"{guid}_1",
            source=n2,
            dest=n1,
            relation=EDGE_RELATION_TO_ENUM[relation2],
            target=EDGE_RELATION_TO_ENUM[relation1],
            distance=0,
        )
        cmd = single_edge(edge1)
        GraphDbApi().run_query(cmd)
        cmd = single_edge(edge2)
        GraphDbApi().run_query(cmd)
        self.context.put(StreckenResetCmd(context=self.content[0]))


class MapDrawOccupiedGuiCmd(Command):
    """Draw occupied edges.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: tuple[str, MapEditor], context: Queue[Command]) -> None:
        """Redraw map.

        Args:
            content (Tuple[str, MapEditor]): (edge_id, map_editor)
            context (Queue[Command]): gui_queue
        """
        super().__init__(content, context)
        self.content: tuple[str, MapEditor]
        self.context: Queue[Command]

    @override
    def run(self) -> None:
        """Draw occupied edge."""
        edge_id, map_editor = self.content
        if edge_id is not None:
            GtCommandSubject().set_next_ts(edge_id)
            weiche = SwitchItem.WEICHE.name
            cmd = f"""
            MATCH(n1:{weiche})-[r]->(n2:{weiche})
            WHERE r.edge_id = '{edge_id}'
            RETURN r.edge_id AS edge_id, type(r) AS ts_source, r.target AS ts_dest, n1.node_id AS source_id, n2.node_id as dest_id
            """
            df = GraphDbApi().run_query(cmd)

            if df.shape[0] == 1:
                self.context.put(DrawOccupiedNetCmd(content=df, context=map_editor))
        self.context.put(DrawCmd(context=map_editor))


class MapFillListGuiCmd(Command):
    """Fill the maps list.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: MapEditor, context: Queue[Command]) -> None:
        """Initialize this command.

        Args:
            content (MapEditor): MapEditor
            context (Queue[Command]): gui_queue
        """
        super().__init__(content, context)
        self.content: MapEditor
        self.context: Queue[Command]

    @override
    def run(self) -> None:
        """Fill the maps list, with data from db."""
        cmd = (
            "MATCH (node:WEICHE) RETURN node.bhf AS bhf, node.name AS name, node.node_id AS node_id"
        )
        df = GraphDbApi().run_query(cmd)[::2]
        df.sort_values(by=["bhf", "name"], inplace=True)
        for _, row in df.iterrows():
            guid = row["node_id"]
            name = f"{row['bhf']}_{row['name']}"
            assert guid[-1] == "0"
            self.context.put(
                MapAddCustomButtonsToListCmd(
                    content=(name, guid, guid[:-1] + "1"), context=self.content
                )
            )


class MapFillCbGuiCmd(Command):
    """Fill the maps combo_box with all edges.

    Args:
        Command (_type_): interface
    """

    def __init__(self, content: QComboBox, context: Queue[Command]) -> None:
        """Initialize this command.

        Args:
            content (QComboBox): combo box
            context (Queue[Command]): gui_queue
        """
        super().__init__(content, context)
        self.content: QComboBox
        self.context: Queue[Command]

    @override
    def run(self) -> None:
        """Fill the maps combo_box."""
        for guid_name in GraphDbApi().edges_tostring():
            self.context.put(AddComboBoxElementCmd(content=guid_name, context=self.content))


class MapDrawConnectTopoGuiCmd(Command):
    """Draw all edges between exit and neutral topopoint.

    Args:
        Command (_type_): interface
    """

    def __init__(
        self,
        content: tuple[pd.DataFrame, MapTsTopopoint, MapTsTopopoint, NetMaker],
        context: Queue[Command],
    ) -> None:
        """Initialize this command.

        Args:
            content (Tuple[pd.DataFrame, neutral_switch, other_switch, NetMaker]): (ecos_df, neutral_switch, other_switch, netmaker)
            context (Queue[Command]): gui_queue
        """
        super().__init__(content, context)
        self.content: tuple[pd.DataFrame, MapTsTopopoint, MapTsTopopoint, NetMaker]
        self.context: Queue[Command]

    @override
    def run(self) -> None:
        """Draw edges in consideration with state of ecos_df."""
        ecos_df, neutral, other, netmaker = self.content
        with ECOS_DF_LOCK:
            state = ecos_df.loc[ecos_df.guid == neutral.guid].state.iloc[0]
        state = int(state)
        if other.coords is not None and neutral.coords is not None:
            u, v = neutral.coords
            ut, vt = other.coords
            snap_to_border = (
                other.relation == EdgeRelation.STRAIGHT.name
                and state == 1
                or other.relation == EdgeRelation.DEFLECTION.name
                and state == 0
            )
            self.context.put(
                DrawGridLineCmd(content=(u, v, ut, vt, snap_to_border), context=netmaker)
            )


class MapDrawConnectTsGuiCmd(Command):
    """Connect two trainswitches.

    Args:
        Command (_type_): interface
    """

    def __init__(
        self,
        content: tuple[dict[str, MapTsTopopoint], NetMaker],
        context: Queue[Command],
    ) -> None:
        """Initialize this command.

        Args:
            content (Tuple[Dict[str, MapTsTopopoint], NetMaker]): (switches from map_editor.zone, netmaker)
            context (Queue[Command]): gui_queue
        """
        super().__init__(content, context)
        self.content: tuple[dict[str, MapTsTopopoint], NetMaker]
        self.context: Queue[Command]

    @override
    def run(self) -> None:
        """Draw a line between two trainswitches if edge exists."""
        switches, net_maker = self.content
        double_vertex = EdgeRelation.DOUBLE_VERTEX.name
        cmd = f"""
        MATCH (n1)-[r]->(n2)\
        WHERE NOT type(r) = '{double_vertex}'\
        RETURN n1.node_id, n2.node_id, r.target AS target, type(r) AS relation
        """
        df = GraphDbApi().run_query(cmd)
        if df.size > 0:
            for _, row in df.iterrows():
                if row["target"] is not None:
                    ts1 = switches.get(f"{row['n1.node_id']}{row['relation']}")
                    ts2 = switches.get(f"{row['n2.node_id']}{row['target']}")
                    if (
                        ts1 is not None
                        and ts2 is not None
                        and ts1.coords is not None
                        and ts2.coords is not None
                    ):
                        u1, v1 = ts1.coords
                        u2, v2 = ts2.coords
                        self.context.put(
                            DrawGridLineCmd(content=(u1, v1, u2, v2, False), context=net_maker)
                        )
