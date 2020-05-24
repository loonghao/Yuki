"""The abstract plugin of the nukestudio export ExcelWriter."""

# Import built-in modules
import abc

# Import third-party modules
from PySide2 import QtWidgets  # pylint: disable=no-module-name


class AbstractHeader:
    """The abstract header of export excel.

    Attributes:
        AbstractHeader.NAME (str): The name will be display in excel.
        AbstractHeader.INSERT_INDEX (int): The index for insert excel.
        AbstractHeader.WIDTH (int): The width length of the info.

    """

    NAME = None
    WIDTH = None
    INDEX = None

    def __init__(self):
        self._settings = {}

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, **dict_):
        self.settings.update(**dict_)

    @abc.abstractmethod
    def write(self, worksheet, row, column, info, settings=None):
        """The custom header write function.

        Args:
            worksheet (yuki.excel_writer.ExcelWriter): The ExcelWriter
                instance.
            row (int): Number of row in excel.
            column (int): Number of column in excel.
            info (info): The item on a Track.
            settings (dict): The settings of the custom header.

        """
        pass
