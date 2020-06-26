# Import built-in modules
import logging

# Import third-party modules
from PySide2 import QtGui

# Import local modules
from yuki import ui_helper
from yuki import widgets
from yuki.excel_writer import ExcelWriter


class Controller(object):

    def __init__(self, model, view, context):
        self._context = context
        self._logger = logging.getLogger(__name__)
        self.view = view
        self.model = model
        self._drag_path = None
        self._settings = self._context.build_settings
        self._app_name = self._settings["app_name"]
        self._video_info = {}
        self.setup()
        self.progress_bar = self.view.progress_bar

    def setup(self):
        self.create_signals()
        self.set_app_style_sheet()

    def create_signals(self):
        self.view.startup_view.file_dropped.connect(self.build_items)
        self.view.push_button.clicked.connect(self.process)
        self.view.build_item_single.connect(self.build_items)

    def set_app_style_sheet(self):
        stylesheet = self._context.get_resource('styles.qss')
        self._context.app.setStyleSheet(open(stylesheet).read())
        self.set_background_image()

    def set_background_image(self):
        bg_image = self._context.get_resource("drag-and-drop.png").replace(
            "\\", "/")
        self.view.startup_view.setPixmap(QtGui.QPixmap(bg_image))

    @ui_helper.progress_bar
    def _export_to_excel(self):
        excel_file_name = self.model.get_excel_file_path(self._drag_path)
        with ExcelWriter(excel_file_name) as worksheet:
            list(
                worksheet.write(0, column_index, header.NAME)
                for column_index, header in enumerate(self.model.headers)
            )
            for column_index, header in enumerate(self.model.headers):
                prog_incr = 100.0 / self.view.table.rowCount()
                for row_num in range(self.view.table.rowCount()):
                    item = self.view.table.item(row_num, column_index)
                    header.write(worksheet, row_num,
                                 column_index,
                                 item.text())
                    self.progress_bar.setValue(int(row_num * prog_incr))

    @ui_helper.catch_error_message
    @ui_helper.wait_cursor
    def process(self):
        self._export_to_excel()
        widgets.MessageDisplay(self._settings["app_name"],
                               "Save excel success!")

    @ui_helper.catch_error_message
    @ui_helper.progress_bar
    @ui_helper.wait_cursor
    def build_items(self, drag_path):
        self._drag_path = drag_path
        all_files = self.model.get_videos(self._drag_path)
        count = len(all_files)
        all_video_info = []
        prog_incr = 100.0 / count
        for index, file_ in enumerate(all_files):
            self._context.app.processEvents()
            all_video_info.append(self.model.get_video_info(file_))
            self.progress_bar.setValue(int(index * prog_incr))
        data = {
            "all_video_info": all_video_info,
            "headers": self.model.get_header()
        }
        self.view.table.set_data(data)
        self.toggle_main_widgets()

    def show(self):
        self.view.show()

    def toggle_main_widgets(self, show_main_widgets=True):
        """Change the layout by hiding/ showing certain objects.

        This gets performed when the user drags a psd file into the window
        so that we show all widgets. If the user clicks the 'X' button at the
        top right, we will change back to the default mode presenting the drop
        label that can be used to drag and drop psd files onto the window.

        Args:
            show_main_widgets (bool, optional): If True, show the view's
                group_main_widgets and hide the startup label, otherwise
                perform this other ways around.

        """
        self.view.group_main_widgets.setVisible(show_main_widgets)
        self.view.startup_view.setVisible(not show_main_widgets)
        self.view.push_button.setVisible(show_main_widgets)
