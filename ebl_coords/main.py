"""Start the EBL-GUI application."""
import sys
from typing import Callable, Optional

from PyQt6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QMainWindow
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from ebl_coords.frontend.main_gui import Ui_MainWindow
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


class MainWindow(QMainWindow):  # type: ignore
    """A Pyqt6 Mainwindow."""

    def __init__(self) -> None:
        """Initialize and show the gui."""
        super().__init__()

        self.graph_db = Api()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # type: ignore

        self.fill_list(self.ui.map_weichen_list, self.example_function)
        self.fill_list(self.ui.weichen_list, self.example_function)
        self.fill_list(self.ui.strecken_list, self.example_function)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())
