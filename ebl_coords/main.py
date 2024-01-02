"""Start the EBL-GUI application."""
import os
import sys
from typing import Callable, List, Optional, Tuple

from PyQt6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QLabel, QListWidget
from PyQt6.QtWidgets import QListWidgetItem, QMainWindow, QPushButton, QVBoxLayout
from PyQt6.QtWidgets import QWidget

from ebl_coords.frontend.main_gui import Ui_MainWindow
from ebl_coords.frontend.zone_maker import ZoneMaker
from ebl_coords.graph_db.api import Api


class CustomBtn(QWidget):  # type: ignore
    """A Custom Container with a QPushButton."""

    def __init__(self, text: str, guid: str, parent: Optional[QWidget] = None):
        """Initialize the button with a guid in a layout."""
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.button = QPushButton(text)
        self.guid = guid
        self.layout.addWidget(self.button)


class CustomZoneSwitchItem(QWidget):  # type: ignore
    """A Custom Container for trainswitches in the zone tab."""

    def __init__(
        self,
        text: str,
        guid: str,
        coords_u: List[str],
        coords_v: List[str],
        parent: Optional[QWidget] = None,
    ):
        """Builds CustomZoneSwitchItem.

        Args:
            text (str): text
            guid (str): guid
            coords_u (str]): coordinates u axis
            coords_v (str]): coordinates v axis
            parent (Optional[QWidget], optional): parent. Defaults to None.
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel(text))

        self.entry = self._generate_location_widget("Eingang", coords_u, coords_v)
        self.layout.addWidget(self.entry)

        self.straight = self._generate_location_widget("Gerade", coords_u, coords_v)
        self.layout.addWidget(self.straight)

        self.deflection = self._generate_location_widget(
            "Ableitung", coords_u, coords_v
        )
        self.layout.addWidget(self.deflection)
        self.guid = guid

    # Ab hier kriege ich über das Element keine Children mehr raus z. B. switchItem.entry.dropdown_u
    def _generate_location_widget(
        self, title: str, coords_u: List[str], coords_v: List[str]
    ) -> QWidget:
        """Builds QWidget for CustomZoneSwitchItem.

        Args:
            title (str): title
            coords_u (str]): coordinates u axis
            coords_v (str]): coordinates v axis

        Returns:
            QWidget: widget containing title and u and y dropdowns
        """
        self.location_widget = QWidget(self)
        self.location_vbox = QVBoxLayout(self)
        self.location_vbox.addWidget(QLabel(title))

        self.coords_u = QWidget(self)
        self.coords_v = QWidget(self)
        self.coords_u_layout = QHBoxLayout(self)
        self.coords_v_layout = QHBoxLayout(self)

        self.dropdown_u, self.dropdown_v = self._generate_combo_boxes_u_v(
            coords_u, coords_v
        )

        self.coords_u_layout.addWidget(QLabel("x-Koordinate"))
        self.coords_u_layout.addWidget(self.dropdown_u)

        self.coords_v_layout.addWidget(QLabel("y-Koordinate"))
        self.coords_v_layout.addWidget(self.dropdown_v)

        self.coords_u.setLayout(self.coords_u_layout)
        self.coords_v.setLayout(self.coords_v_layout)

        self.location_vbox.addWidget(self.coords_u)
        self.location_vbox.addWidget(self.coords_v)
        return self.location_widget.setLayout(self.location_vbox)

    def _generate_combo_boxes_u_v(
        self, items_u: List[str], items_v: List[str]
    ) -> Tuple[QComboBox, QComboBox]:
        """Generates a tuple of comboboxes for widget.

        Args:
            items_u (str]): coordinates u axis
            items_v (str]): coordinates v axis

        Returns:
            Tuple[QComboBox, QComboBox]: tuple of dropdowns, one per axis
        """
        print(items_u, items_v)
        # combo_box_u = self._generate_combo_box(items = items_u, first_item='-')
        combo_box_u = QComboBox(self)
        # combo_box_v = self._generate_combo_box(items = items_v, first_item='-')
        combo_box_v = QComboBox(self)
        return combo_box_u, combo_box_v

    def _generate_combo_box(
        self, items: List[str], first_item: Optional[str]
    ) -> QComboBox:
        """Generates a single combobox with potential 0 index.

        Args:
            items (str]): dropdown items
            first_item (Optional[str]): fist item in list

        Returns:
            QComboBox: combobox
        """
        combo_box = QComboBox(self)
        if first_item:
            combo_box.addItem(first_item)
        combo_box.addItems(items)
        return combo_box


class MainWindow(QMainWindow):  # type: ignore
    """A Pyqt6 Mainwindow."""

    def __init__(self) -> None:
        """Initialize and show the gui."""
        super().__init__()

        self.graph_db = Api()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # type: ignore

        # Initial sind keine Weichen geladen, da keine Zone ausgewählt ist, dies muss noch implementierst werden mit einer Update funktion
        self.fill_list_map(self.ui.map_weichen_list)

        self.fill_list(self.ui.weichen_list, self.example_function)
        self.fill_list(self.ui.strecken_list, self.example_function)

        self.zone_maker = ZoneMaker(self.ui.map_label)
        # Text kann hier von speichern zu generieren & speichern geaendert werden, so dass funktionalität gespiegelt wird
        self.ui.map_zone_speichern_btn.clicked.connect(self.save_zone)
        # self.ui.map_zone_select_combo_box.currentTextChanged.connect(self.load_zone)
        self.populate_zone_dropdown()

        self.show()

    def example_function(self, custom_btn: CustomBtn) -> None:
        """Use this function as an example."""
        print(custom_btn.button.text())
        print(custom_btn.guid)

    def add_btn_to_list(
        self, qlist: QListWidget, text: str, guid: str, foo: Callable[[CustomBtn], None]
    ) -> None:
        """Add a QPushButton to a QList.

        Args:
            qlist (QListWidget): QListWidget
            text (str): display text of the button
            guid (str): guid
            foo (Callable[[CustomBtn], None]): bound to button.clicked
        """
        item = QListWidgetItem(qlist)
        custom_btn = CustomBtn(text, guid)
        custom_btn.button.released.connect(lambda: foo(custom_btn))
        item.setSizeHint(custom_btn.sizeHint())
        qlist.setItemWidget(item, custom_btn)

    def add_switch_item_to_list(self, qlist: QListWidget, text: str, guid: str) -> None:
        """Add a CustomZoneSwitchItem to a QList.

        Args:
            qlist (QListWidget): QListWidget
            text (str): switch_name
            guid (str): guid
        """
        item = QListWidgetItem(qlist)
        custom_switch_item = CustomZoneSwitchItem(text, guid, [], [])
        item.setSizeHint(custom_switch_item.sizeHint())
        qlist.setItemWidget(item, custom_switch_item)

    def fill_list(self, qlist: QListWidget, foo: Callable[[CustomBtn], None]) -> None:
        """Fill given list with train switches from the graph db.

        Args:
            qlist (QListWidget): QListWidget
            foo (Callable[[CustomBtn], None]): bound to button.clicked
        """
        cmd = "MATCH (node:WEICHE) RETURN node.bhf, node.name, node.node_id"
        df = self.graph_db.run_query(cmd)[::2]
        for _, row in df.iterrows():
            self.add_btn_to_list(
                qlist,
                text=f"{row['node.bhf']}_{row['node.name']}",
                guid=row["node.node_id"],
                foo=foo,
            )

    def fill_list_map(self, qlist: QListWidget) -> None:
        """Fill given list with CustomZoneSwitchItem based on the switches from the graph_db.

        Args:
            qlist (QListWidget): QListWidget
        """
        cmd = "MATCH (node:WEICHE) RETURN node.bhf, node.name, node.node_id"
        df = self.graph_db.run_query(cmd)[::2]
        for _, row in df.iterrows():
            self.add_switch_item_to_list(
                qlist,
                text=f"{row['node.bhf']}_{row['node.name']}",
                guid=row["node.node_id"],
            )

    def save_zone(self) -> None:
        """Saves the current zone as a json file."""
        zone_name = self.ui.map_zonename_txt.text()
        zone_width = self.ui.map_zone_width.value()
        zone_height = self.ui.map_zone_height.value()
        print(zone_name, zone_width, zone_height)
        self.zone_maker.draw_grid(zone_width, zone_height)
        # zone_json = Zone(
        #    zone_name,
        #    zone_width,
        #    zone_height,
        #    dict["keys_width"],
        #    dict["keys_height"],
        #    None,
        # )
        # Lists are not serializable with dataclass_json
        # json_string = zone_json.to_json()
        # with open(f'./data/frontend/{zone_name}.json', 'w') as file:
        #    file.write(json_string)
        self.populate_zone_dropdown()
        # map.draw_grid_line(0, 0, 20, 5)

    def populate_zone_dropdown(self) -> None:
        """Populates the dropdown list with all existing zones."""
        zone_file_list = os.listdir("./ebl_coords/frontend/zone_data")
        zones = list(map(lambda zone: zone.split(".")[0], zone_file_list))
        self.ui.map_zone_select_combo_box.clear()
        for zone in zones:
            self.ui.map_zone_select_combo_box.addItme(zone)

    # def load_zone(self, selected_zone: str):
    #    """Loads a zone from the specified json file


#
#    Args:
#        selected_zone (str): zone selected in dropdown
#    """
#    zone_json = open(f'./data/frontend/{selected_zone}.json')
#    zone = Zone.from_json(zone_json)
#    self.ui.map_zonename_txt.text = zone.name
#    self.ui.map_zone_width.value = zone.width
#    self.ui.map_zone_height.value = zone.height
#    self.zone_maker.draw_grid(zone.width, zone.height)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())
