# -*- coding: utf-8 -*-
"""
module author: Long Hao <hoolongvfx@gmail.com>
"""
# Import built-in modules
import contextlib
import logging
import os
import re
import subprocess as sp
import sys

# Import third-party modules
import xlsxwriter

# Import local modules
# This need first load
from config import APP_NAME, APP_VERSION, resource_path

os.environ['APP_CONFIG'] = resource_path()

import hz.toolkit as htk
from PySide import QtCore, QtGui
from hz.awesome_ui.widgets import AwesomeSplashScreen
from hz.awesome_ui.widgets import MessageDisplay
from hz.awesome_ui.widgets import RenderAwesomeUI

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

_FFMPEG_CMD = resource_path('ffmpeg/ffmpeg.exe')


class MainGUI(QtGui.QWidget):

    def __init__(self):
        super(MainGUI, self).__init__()
        RenderAwesomeUI(resource_path('GUI.ui'), self)
        self.table = QtGui.QTableWidget(self)
        self.verticalLayout.addWidget(self.table)
        self.settings = htk.load_yaml(
            resource_path('settings/config.yaml'), True)
        self.setAcceptDrops(True)
        header = self.table.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        self.setWindowTitle('{} v{}'.format(APP_NAME, APP_VERSION))
        self.drag_file = None
        self.pushButton.clicked.connect(self.export_csv)
        self.progressBar.hide()
        self.setWindowIcon(QtGui.QIcon(resource_path("logo.ico")))
        self.pushButton.hide()
        bg_image = resource_path("bg.png").replace('\\', '/')
        style_sheet = """QTableWidget
         {
            background: url("<bg>");
            background-repeat: no-repeat;
            background-position: center;
            background-attachment: scroll;
            color: rgb(250, 250, 250);
         }""".replace("<bg>", bg_image)
        self.table.setStyleSheet(style_sheet)

    def export_csv(self):
        self.progressBar.setValue(0)
        self.progressBar.show()
        if self.drag_file:
            excel_file_name = os.path.join(self.drag_file, 'shot_info.xlsx')
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
                        thumb_file = thumb_file.replace('//', '/')
                        htk.create_missing_directories(
                            os.path.dirname(thumb_file))
                        command = [
                            _FFMPEG_CMD, '-y', '-i', file_path, '-f', 'image2',
                            '-t', '0.001', '-vframes', '1', '-vf',
                            'scale=300:-1:sws_dither=ed', thumb_file
                        ]
                        try:
                            sp.check_call(command)
                        except Exception as e:
                            LOGGER.error('{}:{}'.format(e, mov_name))
                        worksheet.set_row(row + 1, 130)
                        if thumb_file:
                            worksheet.insert_image(
                                row + 1, 0, thumb_file, {
                                    "x_scale": 0.9,
                                    'x_offset': 10,
                                    'y_offset': 10,
                                    "y_scale": 0.9
                                })
                        item = self.table.item(row, 5)
                        value = item.text()
                        worksheet.write(row + 1, 1, value, format_)
                        for x in range(0, 5):
                            item = self.table.item(row, x)
                            value = item.text()
                            worksheet.write(row + 1, x + 2, value, format_)
                        APP.processEvents()
                        self.progressBar.setValue(int(row * prog_incr))
            self.progressBar.hide()
            MessageDisplay(APP_NAME, "save excel success!")

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

    def dropEvent(self, event):
        # self.search_text.deselect()
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

    def build_items(self):
        self.pushButton.show()
        self.table.setStyleSheet("""QTableWidget {
                           color: rgb(250, 250, 250);
                           }""")
        self.table.setRowCount(0)
        self.table.clearContents()
        self.progressBar.setValue(0)
        self.progressBar.show()
        all_files = []
        # all_files =
        for file_ in os.listdir(self.drag_file):
            ext = htk.get_file_ext(file_)
            if ext in self.settings.format:
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
                        file_path = file_path.replace('//', '/')
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
                        self.progressBar.setValue(int(row * prog_incr))
                except Exception as e:
                    LOGGER.error(e)
                    LOGGER.error(layer)
        else:
            LOGGER.warning('not find any data.')

        self.progressBar.hide()

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
                sp.Popen(command, stdout=DEVNULL, stderr=sp.PIPE)) as pipe:
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
    GUI = MainGUI()
    LOGGER = logging.getLogger('octopus')
    HANDLER = logging.StreamHandler()
    HANDLER.setLevel(logging.DEBUG)
    FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s: %(levelname)s  %(message)s')
    HANDLER.setFormatter(FORMATTER)
    LOGGER.addHandler(HANDLER)
    IMGAE_PATH = resource_path('splash_screen.png')
    SPLASH = AwesomeSplashScreen(IMGAE_PATH)
    APP.processEvents()
    APP.setApplicationVersion(APP_VERSION)
    SPLASH.showMessage("version: {}".format(APP_VERSION))
    SPLASH.effect()
    APP.setApplicationName(APP_NAME)
    APP.processEvents()
    GUI.show()
    SPLASH.finish(GUI)
    APP.exec_()
