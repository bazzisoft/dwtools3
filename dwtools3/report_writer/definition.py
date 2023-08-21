from .enums import OutputType
from .formats import DefaultFormatter
from .styles import Style
from .utils import ColumnDef
from .writers.csv import CSVReportWriter
from .writers.excel import ExcelReportWriter
from .writers.html import HTMLReportWriter


class ReportDefinition:
    """
    Defines the columns, styles and data formats of the report.

    Styles cascade in a similar manner to CSS. Order
    of precedence is: Individual cell styles, row styles, column styles
    and finally the default style.
    """

    def __init__(self):
        self.empty_style = Style()
        self.default_style = self.empty_style
        self.formatter = DefaultFormatter()
        self.columns = []
        self.column_map = {}

    def set_formatter(self, formatter):
        """
        Sets the ``IFormatter`` subclass to use for formatting data
        values in this report.
        """
        self.formatter = formatter

    def set_default_style(self, style):
        """
        Sets the default ``Style`` subclass to use styling all cells written
        by the report.
        """
        self.default_style = style

    def add_column(self, field_name, label=None, width=None, colstyle=None):
        """
        Adds a column to the report.

        :param str field_name: The dict key of this column in the data passed to ``writerow()``.
        :param str label: An optional label to output in the heading row.
        :param int width: An optional 'em' width for this column.
        :param Style colstyle: An optional style to apply to this entire column.
        """
        assert field_name not in self.column_map
        index = len(self.columns)
        colstyle = colstyle or self.empty_style
        self.columns.append(ColumnDef(index, field_name, label, width, colstyle))
        self.column_map[field_name] = index

    def open_file_for_writer(self, filename, output_type):
        """
        Opens the specified file with the correct mode for the
        selected output type.

        :param str filename: The file to open.
        :param OutputType output_type: The output type we're going to write.
        """
        if output_type in (OutputType.EXCEL,):
            return open(filename, "wb")
        elif output_type in (OutputType.CSV,):
            return open(filename, "w", newline="", encoding="utf-8")
        else:
            return open(filename, "w", encoding="utf-8")

    def create_writer(self, filename_or_stream, output_type):
        """
        Creates an ``IReportWriter`` object that can be used to write
        the report data to a stream.

        If passing a stream, it must be opened with the correct mode
        depending on the output type. See: ``open_file_for_writer()``.

        :param filename_or_stream: The filename or stream to write to.
        :param OutputType output_type: The data format to write the report in.
        """
        if isinstance(filename_or_stream, str):
            stream = self.open_file_for_writer(filename_or_stream, output_type)
            close_stream = True
        else:
            stream = filename_or_stream
            close_stream = False

        if output_type == OutputType.EXCEL:
            return ExcelReportWriter(self, stream, close_stream)
        elif output_type == OutputType.CSV:
            return CSVReportWriter(self, stream, close_stream)
        elif output_type == OutputType.HTML:
            return HTMLReportWriter(self, stream, close_stream)
        elif output_type == OutputType.HTML_FULL_PAGE:
            return HTMLReportWriter(self, stream, close_stream, full_page=True)
        else:
            assert False, "Invalid output type {}".format(output_type)

    def list_fields(self, exclude_datatypes=None):
        """
        Returns a list of all column field names defined.
        """
        exclude_datatypes = set(exclude_datatypes) if exclude_datatypes else set()
        return [
            c.field_name for c in self.columns if c.colstyle.get_datatype() not in exclude_datatypes
        ]

    def list_fields_for_writer(self, writer):
        """
        Returns a list of all column field names visible for the specified writer.
        """
        return self.list_fields(exclude_datatypes=writer.list_excluded_datatypes())
