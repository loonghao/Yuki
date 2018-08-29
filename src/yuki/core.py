# -*- coding: utf-8 -*-
"""
module author: Long Hao <hoolongvfx@gmail.com>
"""
# Import built-in modules
import contextlib
import logging
import os
import re
import subprocess
import sys

# Import third-party modules
import xlsxwriter
from PySide import QtCore, QtGui

# Import local modules
from yuki.config import APP_NAME
from yuki.config import APP_VERSION
from yuki.config import EXCEL_NAME
from yuki.config import FORMATS
from yuki.config import resource_path
from yuki.utils import catch_error_message
from yuki.utils import create_missing_directories
from yuki.utils import get_file_ext
from yuki.utils import load_style_sheet
from yuki.utils import progress_bar
from yuki.utils import wait_cursor
from yuki.widgets import MessageDisplay

_FFMPEG_CMD = resource_path('resources/ffmpeg/ffmpeg.exe')


class YukiGUI(QtGui.QWidget):
    def __init__(self):
        super(YukiGUI, self).__init__()
        self.setMinimumHeight(616)
        self.setMinimumWidth(655)
        verticalLayout_3 = QtGui.QVBoxLayout()
        verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout = QtGui.QVBoxLayout()
        self.progress_bar = QtGui.QProgressBar()
        self.pushButton = QtGui.QPushButton('export to excel')
        self.table = QtGui.QTableWidget(self)
        self.verticalLayout.addWidget(self.table)
        verticalLayout_2.addWidget(self.progress_bar)
        verticalLayout_2.addWidget(self.pushButton)
        verticalLayout_3.addLayout(self.verticalLayout)
        verticalLayout_3.addLayout(verticalLayout_2)
        self.setLayout(verticalLayout_3)
        self.setAcceptDrops(True)
        header = self.table.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        self.setWindowTitle('{} v{}'.format(APP_NAME, APP_VERSION))
        self.drag_file = None
        self.pushButton.clicked.connect(self.export_csv)
        self.progress_bar.hide()
        self.setWindowIcon(
            QtGui.QIcon(resource_path("resources/images/logo.ico")))
        self.pushButton.hide()
        bg_image = resource_path("resources/images/bg.png").replace('\\', '/')
        style_sheet = """QTableWidget
         {
            background: url("<bg>");
            background-repeat: no-repeat;
            background-position: center;
            background-attachment: scroll;
            color: rgb(250, 250, 250);
         }""".replace("<bg>", bg_image)
        self.table.setStyleSheet(style_sheet)

    @catch_error_message
    @progress_bar
    @wait_cursor()
    def export_csv(self):
        if self.drag_file:
            excel_file_name = os.path.join(self.drag_file, EXCEL_NAME)
            with xlsxwriter.Workbook(excel_file_name) as workbook:
                worksheet = workbook.add_worksheet()
                format_ = workbook.add_format()
                format_.set_align('center')
                format_.set_bold()
                format_.set_align('vcenter')
                worksheet.set_row(0, 18)
                worksheet.set_column(0, 1, 40)
                worksheet.set_column(1, 6, 30)
                worksheet.write(0, 0, 'Thumbnail', format_)
                worksheet.write(0, 1,
                                self.table.horizontalHeaderItem(5).text(),
                                format_)
                for index in range(0, 5):
                    worksheet.write(
                        0, index + 2,
                        self.table.horizontalHeaderItem(index).text(), format_)

                prog_incr = 100.0 / self.table.rowCount()
                for row in range(self.table.rowCount()):
                    item_ = self.table.item(row, 5)
                    if item_:
                        file_path = item_.file_path
                        mov_name = os.path.basename(file_path).split('.')[0]
                        thumb_file = os.path.join(self.drag_file, 'thumb',
                                                  '{}.jpg'.format(mov_name))
                        thumb_file = thumb_file.replace('/', '\\')
                        folder = os.path.dirname(thumb_file)
                        create_missing_directories(folder)
                        command = list()
                        command.append(_FFMPEG_CMD)
                        command.append('-y')
                        command.append('-i')
                        command.append(file_path)
                        command.append('-f')
                        command.append('image2')
                        command.append('-t')
                        command.append('0.001')
                        command.append('-vframes')
                        # Make Thumb image in that frame.
                        command.append('10')
                        command.append('-vf')
                        # Thumb file scale size.
                        command.append('scale=300:-1:sws_dither=ed')
                        # Thumb save location.
                        command.append(thumb_file)
                        LOGGER.debug(subprocess.list2cmdline(command))
                        try:
                            subprocess.check_output(command)
                        except subprocess.CalledProcessError as err:
                            LOGGER.error('{}:{}'.format(err, mov_name))
                        worksheet.set_row(row + 1, 130)
                        if thumb_file:
                            image_format = {
                                    "x_scale": 0.9,
                                    'x_offset': 10,
                                    'y_offset': 10,
                                    "y_scale": 0.9
                            }
                            worksheet.insert_image(row + 1,
                                                   0,
                                                   thumb_file,
                                                   image_format)
                        item = self.table.item(row, 5)
                        value = item.text()
                        worksheet.write(row + 1, 1, value, format_)
                        for x in range(0, 5):
                            item = self.table.item(row, x)
                            value = item.text()
                            worksheet.write(row + 1, x + 2, value, format_)
                        APP.processEvents()
                        self.progress_bar.setValue(int(row * prog_incr))
            self.progress_bar.hide()
            MessageDisplay(APP_NAME, "Save excel success!")

    # Code reference from :
    # https://github.com/menpo/menpo/blob/master/menpo/io/input/video.py
    @contextlib.contextmanager
    def _call_subprocess(self, process):
        r"""
        Call a subprocess and automatically clean up/wait for the various
        pipe interfaces, {stderr, stdout, stdin}.
        Parameters
        ----------
        process : `subprocess.POpen`
            The subprocess POpen object to automatically close.
        Yields
        ------
        The ``subprocess.POpen`` object back for processing.
        """
        try:
            yield process
        finally:
            for stream in (process.stdout, process.stdin, process.stderr):
                if stream:
                    stream.close()
            process.wait()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    @catch_error_message
    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            if event.source() is self:
                event.setDropAction(QtCore.Qt.MoveAction)
            else:
                event.setDropAction(QtCore.Qt.CopyAction)
        url = event.mimeData().urls()
        if url:
            for url in event.mimeData().urls():
                self.drag_file = url.toLocalFile()
                if self.drag_file:
                    if os.path.isdir(self.drag_file):
                        self.build_items()
                    else:
                        LOGGER.warning('please drop the folder try again.')

    @catch_error_message
    @progress_bar
    @wait_cursor()
    def build_items(self):
        all_files = []
        self.pushButton.show()
        sheet = """QTableWidget
         {
           color: rgb(250, 250, 250);
         }
         """
        self.table.setStyleSheet(sheet)
        self.table.setRowCount(0)
        self.table.clearContents()
        for file_ in os.listdir(self.drag_file):
            ext = get_file_ext(file_)
            if ext in FORMATS:
                all_files.append(file_)
        if all_files:
            self.table.setColumnCount(6)
            prog_incr = 100.0 / len(all_files)
            for layer, row in zip(all_files, range(0, len(all_files))):
                try:
                    item = QtGui.QTableWidgetItem('File Name')
                    self.table.setHorizontalHeaderItem(5, item)
                    LOGGER.info('start get video info from {}'.format(layer))
                    info = self.video_infos_ffmpeg(
                        os.path.join(self.drag_file, layer))
                    current_row_count = self.table.rowCount()
                    self.table.setRowCount(current_row_count + 1)
                    if info:
                        layer_item = QtGui.QTableWidgetItem(layer)
                        file_path = os.path.join(self.drag_file, layer)
                        file_path = file_path.replace('/', '\\')
                        layer_item.file_path = file_path

                        self.table.setItem(row, 5, layer_item)
                        head_ = ['duration', 'width', 'height', 'frames',
                                 'fps']
                        for index, name in enumerate(head_):
                            item = QtGui.QTableWidgetItem(name)
                            self.table.setHorizontalHeaderItem(index, item)
                            layer_item = QtGui.QTableWidgetItem(
                                str(info[name]))

                            self.table.setItem(row, index, layer_item)
                        APP.processEvents()
                        self.progress_bar.setValue(int(row * prog_incr))
                except Exception as e:
                    LOGGER.error(e)
                    LOGGER.error(layer)
        else:
            message = 'Did not found any data.'
            LOGGER.warning(message)
            MessageDisplay(APP_NAME, message, MessageDisplay.WARNING)

    # Code reference from :
    # https://github.com/menpo/menpo/blob/master/menpo/io/input/video.py
    def video_infos_ffmpeg(self, filepath):
        r"""
        Parses the information from a video using ffmpeg.
        Uses subprocess to get the information through a pipe.
        Parameters
        ----------
        filepath : `Path`
            absolute path to the video file which information to extract
        Returns
        -------
        infos : `dict`
            keys are width, height (size of the frames)
            duration (duration of the video in seconds)
            n_frames
        """

        # Read information using ffmpeg - the call below intentionally causes
        # an error about no output from FFMPEG in order to terminate faster - hence
        # reading the output from stderr.
        command = [_FFMPEG_CMD, '-i', str(filepath), '-']

        with self._call_subprocess(
                subprocess.Popen(command, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)) as pipe:
            raw_infos = pipe.stderr.read()
        # Note: we use '\d+\.?\d*' so we can match both int and float for the fps
        video_info = re.search(
            r"Video:.*(?P<width> \d+)x(?P<height>\d+).*(?P<fps> \d+\.?\d*) fps",
            raw_infos, re.DOTALL).groupdict()

        # Some videos don't have a valid duration
        time = re.search(
            r"Duration:\s(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),",
            raw_infos, re.DOTALL)
        if time is None:
            raise ValueError('Unable to determine duration for video - please '
                             'install and use ffprobe for accurate yuki count '
                             'computation.')

        # Get the duration in seconds and convert size to ints
        time = time.groupdict()
        hours = float(time['hours'])
        minutes = float(time['minutes'])
        seconds = float(time['seconds'])

        duration = 60 * 60 * hours + 60 * minutes + seconds

        fps = round(float(video_info['fps']))
        n_frames = round(duration * fps)
        width = int(video_info['width'])
        height = int(video_info['height'])

        # Create the resulting dictionary
        infos = {
            'fps': fps,
            'duration': duration,
            'width': width,
            'height': height,
            'frames': n_frames
        }

        return infos


if __name__ == '__main__':
    APP = QtGui.QApplication(sys.argv)
    GUI = YukiGUI()
    LOGGER = logging.getLogger(__name__)
    IMGAE_PATH = resource_path('splash_screen.png')
    # SPLASH = AwesomeSplashScreen(IMGAE_PATH)
    APP.processEvents()
    APP.setApplicationVersion(APP_VERSION)
    # SPLASH.showMessage("version: {}".format(APP_VERSION))
    # SPLASH.effect()
    APP.setStyleSheet(
        load_style_sheet(resource_path('resources/css/core.css')))
    APP.setApplicationName(APP_NAME)
    APP.processEvents()
    GUI.show()
    # SPLASH.finish(GUI)
    APP.exec_()
