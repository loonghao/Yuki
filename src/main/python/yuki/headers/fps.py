"""The clip of excel header."""

# Import local module
from yuki.header import AbstractHeader


class Header(AbstractHeader):
    """The clip header of export excel.

    Attributes:
        Header.NAME (str): The name will be display in excel.

    """
    NAME = 'FPS'

    def write(self, worksheet, row, column, info, settings=None):
        """Write the clip info in the excel.

        Args:
            worksheet (yuki.excel_writer.ExcelWriter): The Excel
                instance.
            row (int): Number of row in excel.
            column (int): Number of column in excel.
            track_item (hiero.core.TrackItem): The item on a Track.

        """
        worksheet.write(row + 1, column, info)
