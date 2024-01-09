"""Custom Widgets and helper functions for PyQt-Gui."""
from typing import Callable, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QListWidgetItem
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from ebl_coords.decorators import override
from ebl_coords.graph_db.api import Api
from ebl_coords.graph_db.data_elements.edge_relation_enum import EdgeRelation


class ClickableLabel(QLabel):  # type: ignore
    """A clickable QLabel."""

    clicked = pyqtSignal()

    def __init__(self) -> None:
        """Initialize clock event."""
        super().__init__()
        self.click_event: QMouseEvent

    @override
    def mousePressEvent(self, event: QMouseEvent) -> None:  # pylint: disable=C0103
        """Evoke connected click event and store it.

        Args:
            event (QMouseEvent): mouse event
        """
        self.click_event = event
        self.clicked.emit()


class CustomBtn(QWidget):  # type: ignore
    """A Custom Container with a QPushButton."""

    def __init__(self, text: str, guid: str, parent: Optional[QWidget] = None):
        """Initialize the button with a guid in a layout."""
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.button = QPushButton(text)
        self.guid = guid
        self.layout.addWidget(self.button)


class CustomZoneContainer(QWidget):  # type: ignore
    """A Custom Container with a label and three QPushButtons."""

    def __init__(
        self, text: str, guid_0: str, guid_1: str, parent: Optional[QWidget] = None
    ) -> None:
        """Initialize the container from a double node.

        Args:
            text (str): Naming label
            guid_0 (str): id from node_0
            guid_1 (str): id from node_1
            parent (Optional[QWidget]): parent. Defaults to None.
        """
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.name_label = QLabel(text)
        self.neutral_btn = QPushButton(EdgeRelation.NEUTRAL.value)
        self.deflection_btn = QPushButton(EdgeRelation.DEFLECTION.value)
        self.straight_btn = QPushButton(EdgeRelation.STRAIGHT.value)
        self.guid_0 = guid_0
        self.guid_1 = guid_1
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.neutral_btn)
        self.layout.addWidget(self.straight_btn)
        self.layout.addWidget(self.deflection_btn)


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
    df.sort_values(by=["node.bhf", "node.name"], inplace=True)
    for _, row in df.iterrows():
        add_btn_to_list(
            qlist,
            text=f"{row['node.bhf']}_{row['node.name']}",
            guid=row["node.node_id"],
            foo=foo,
        )
