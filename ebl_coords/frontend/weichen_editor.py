"""Weichen Editor."""
from typing import Optional

from ebl_coords.decorators import override
from ebl_coords.frontend.custom_widgets import CustomBtn, fill_list
from ebl_coords.frontend.editor import Editor
from ebl_coords.frontend.main_gui import Ui_MainWindow
from ebl_coords.graph_db.api import Api


class WeichenEditor(Editor):
    """Editor for train switches.

    Args:
        Editor (_type_): Base Editor class.
    """

    def __init__(self, ui: Ui_MainWindow, graph_db: Api) -> None:
        """Bind rest Button and fill list with data from the db.

        Args:
            ui (Ui_MainWindow): main window
            graph_db (Api): api of graph database
        """
        super().__init__(ui=ui, graph_db=graph_db)

        self.ui.weichen_new_btn.clicked.connect(self.reset)
        self.selected_ts: Optional[str] = None

        fill_list(self.graph_db, self.ui.weichen_list, self.select_ts)

    @override
    def reset(self) -> None:
        """Clear all textfields and deselect the active trainswitch."""
        self.ui.weichen_weichenname_txt.clear()
        self.ui.weichen_dcc_txt.clear()
        self.ui.weichen_bhf_txt.clear()
        self.selected_ts = None

    def select_ts(self, custom_btn: CustomBtn) -> None:
        """Select a train switch.

        Args:
            custom_btn (CustomBtn): source button
        """
        print(custom_btn.text())
