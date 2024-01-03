"""Start the EBL-GUI application."""
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from ebl_coords.frontend.main_gui import Ui_MainWindow
from ebl_coords.frontend.map_editor import MapEditor
from ebl_coords.frontend.strecken_editor import StreckenEditor
from ebl_coords.frontend.weichen_editor import WeichenEditor
from ebl_coords.graph_db.api import Api


class MainWindow(QMainWindow):  # type: ignore
    """A Pyqt6 Mainwindow."""

    def __init__(self) -> None:
        """Initialize and show the gui."""
        super().__init__()

        self.graph_db = Api()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # type: ignore

        self.strecken_editor = StreckenEditor(self.ui, self.graph_db)
        self.weichen_editor = WeichenEditor(
            self.ui, self.graph_db, self.strecken_editor
        )
        self.map_editor = MapEditor(self.ui, self.graph_db)

        self.show()

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
