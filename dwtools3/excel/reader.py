import openpyxl
from collections import OrderedDict
from openpyxl.utils.exceptions import InvalidFileException


class ExcelReaderError(IOError):
    """
    Raised if an invalid XLSX is opened, or invalid sheets are read.
    """
    pass


class ExcelReader:
    """
    Opens and reads an Excel XLSX file.

    :param filename_or_stream: The path to the XLSX file or any stream
        with the file contents.
    """
    def __init__(self, filename_or_stream=None):
        try:
            self.workbook = openpyxl.load_workbook(filename_or_stream, read_only=True, data_only=True)
        except (OSError, InvalidFileException) as e:
            raise ExcelReaderError(str(e)) from e

    def num_sheets(self):
        """
        Returns the number of sheets in the workbook.
        """
        return len(self.workbook.get_sheet_names())

    def list_sheets(self):
        """
        Returns the names of the sheets in the workbook.
        """
        return self.workbook.get_sheet_names()

    def read_sheet(self, index_or_name, header_row=False):
        """
        Returns a generator of all data in the sheet, referenced by index or name.

        :param int/str index_or_name: The index or name of the sheet to read.
        :param bool header_row: Whether the Excel sheet has a header row. If yes, returns
            each subsequent row as an ``OrderedDict``.
        """
        if isinstance(index_or_name, int):
            try:
                index_or_name = self.workbook.get_sheet_names()[index_or_name]
            except IndexError:
                raise ExcelReaderError('Sheet with index {} does not exist.'.format(index_or_name)) from None

        try:
            sheet = self.workbook[index_or_name]
        except KeyError:
            raise ExcelReaderError('Sheet with name "{}" does not exist.'.format(index_or_name)) from None

        it = iter(sheet.rows)

        if header_row:
            try:
                header_fields = [c.value for c in next(it)]
            except StopIteration:
                return

        for row in it:
            data = [c.value for c in row]
            if header_row:
                data = OrderedDict(zip(header_fields, data))
            yield data
