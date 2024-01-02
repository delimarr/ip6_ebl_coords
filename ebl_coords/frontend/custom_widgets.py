"""Custom Widgets and helper functions for PyQt-Gui."""
from typing import Callable, Optional

from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QPushButton, QVBoxLayout
from PyQt6.QtWidgets import QWidget

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


def add_btn_to_list(
    qlist: QListWidget, text: str, guid: str, foo: Callable[[CustomBtn], None]
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


def fill_list(
    graph_db: Api, qlist: QListWidget, foo: Callable[[CustomBtn], None]
) -> None:
    """Fill given list with train switches from the graph db.

    Args:
        graph_db (Api): api of graph database
        qlist (QListWidget): QListWidget
        foo (Callable[[CustomBtn], None]): bound to button.clicked
    """
    cmd = "MATCH (node:WEICHE) RETURN node.bhf, node.name, node.node_id"
    df = graph_db.run_query(cmd)[::2]
    for _, row in df.iterrows():
        add_btn_to_list(
            qlist,
            text=f"{row['node.bhf']}_{row['node.name']}",
            guid=row["node.node_id"],
            foo=foo,
        )
