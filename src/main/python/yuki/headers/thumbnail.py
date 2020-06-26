"""The clip of excel header."""
# Import built-in modules
import os

# Import local module
from yuki.header import AbstractHeader


class Header(AbstractHeader):
    """The clip header of export excel.

    Attributes:
        Header.NAME (str): The name will be display in excel.

    """
    NAME = 'Thumbnail'

    def write(self, worksheet, row, column, content):
        """Write the clip info in the excel.

        Args:
            worksheet (yuki.excel_writer.ExcelWriter): The Excel
                instance.
            row (int): Number of row in excel.
            column (int): Number of column in excel.
            content (str): The content will be written.

        """
        if not os.path.isfile(content):
            info = "OFFLINE"
            return worksheet.write(row + 1, column, info)
        worksheet.insert_image(row + 1, column, content)
