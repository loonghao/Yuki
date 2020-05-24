# Import built-in modules
import os
import logging

# Import third-party modules
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

# Import local modules
from yuki.widgets import CustomTableView
from yuki.widgets import DropLabel


class View(QtWidgets.QWidget):
    build_item_single = QtCore.Signal(str)

    def __init__(self):
        super(View, self).__init__()
        self.drag_file = None
        self.master_layout = QtWidgets.QVBoxLayout(self)
        self.group_main_widgets = QtWidgets.QGroupBox(self)
        self.startup_view = DropLabel()
        self.table = CustomTableView()
        self.progress_bar = QtWidgets.QProgressBar()
        self.push_button = QtWidgets.QPushButton("Export to excel")

        self.setup_ui()

    def setup_ui(self):
        self.setMinimumHeight(616)
        self.setMinimumWidth(655)

        self.progress_bar.hide()
        self.push_button.setVisible(False)
        self.setup_layout()
        self.group_main_widgets.setVisible(False)

    def setup_layout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.push_button)
        self.group_main_widgets.setLayout(layout)
        self.master_layout.addWidget(self.group_main_widgets)
        self.master_layout.addWidget(self.startup_view)
        self.setLayout(self.master_layout)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    @staticmethod
    def _get_valid_url(event):
        """Accepts only single existing directory with any kind of content:
        files, subdirectories etc.

        Args:
            event (QtGui.QDropEvent): Event from drag and drop process.

        Returns:
            str: Valid url if the content is valid.

        """
        if event.mimeData().hasUrls and (len(event.mimeData().urls()) == 1):
            url = event.mimeData().urls()[0]
            path = str(url.toLocalFile())
            if os.path.exists(path) and os.path.isdir(path):
                return path
        return None

    def dropEvent(self, event):
        path = self._get_valid_url(event)
        if path:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            self.build_item_single.emit(path)
        else:
            logger = logging.getLogger(__name__)
            logger.warning('Please drop the folder try again.')
