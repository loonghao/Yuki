"""The ExcelWriter wrapper function for export ExcelWriter."""

# Import third-party modules
import xlsxwriter


class ExcelWriter(object):
    def __init__(self, excel_file_name):
        self._workbook = xlsxwriter.Workbook(excel_file_name)
        self.worksheet = self._workbook.add_worksheet()
        self.worksheet.set_row(0, 18)
        self.worksheet.set_column(0, 0, 60)
        self.worksheet.set_column(1, 8, 30)
        self.worksheet.set_column(9, 10, 150)
        self.format = self._workbook.add_format()
        self.format.set_align('center')
        self.format.set_bold()
        self.format.set_align('vcenter')
        self.file_path = excel_file_name

    @property
    def bold(self):
        return self._workbook.add_format({'bold': True})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(self._workbook.formats)
        self._workbook.close()

    def write(self, row, column, data):
        self.set_row(row)
        self.worksheet.write(row, column, data, self.format)

    def set_row(self, row_num):
        self.worksheet.set_row(row_num, 203)

    def insert_image(self, row_num, column, image_path):
        self.set_row(row_num)
        self.worksheet.insert_image(row_num, column,
                                    image_path,
                                    {
                                        "x_scale": 0.9,
                                        'x_offset': 10,
                                        'y_offset': 10,
                                        "y_scale": 0.9
                                    })
