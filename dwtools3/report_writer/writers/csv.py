import csv
from .base import IReportWriter
from ..enums import DataType


class CSVReportWriter(IReportWriter):
    """
    Writes a report in the CSV format.

    This writer expects a string stream, so files must be opened
    in text mode, viz::

        with open(path, 'w', newline='', encoding='utf-8') as f:
    """
    def __init__(self, definition, stream, close_stream):
        super().__init__(definition, stream, close_stream)
        self.writer = csv.DictWriter(stream, fieldnames=self.definition.list_fields(exclude_datatypes=(DataType.HTML,)), extrasaction='ignore')

    def writerow(self, rowdict, styledict=None, rowstyle=None):
        output = {}
        for col in self.definition.columns:
            cellstyle = styledict.get(col.field_name) if styledict else None
            value = rowdict.get(col.field_name, '')
            datatype = self._determine_datatype(cellstyle, rowstyle, col.colstyle)
            output[col.field_name] = self.definition.formatter.format(datatype, value)

        self.writer.writerow(output)

    def _determine_datatype(self, cellstyle, rowstyle, colstyle):
        d = self.definition.default_style.get_datatype()
        d = colstyle.get_datatype() or d
        d = (rowstyle and rowstyle.get_datatype()) or d
        d = (cellstyle and cellstyle.get_datatype()) or d
        return d
