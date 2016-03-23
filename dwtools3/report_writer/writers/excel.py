import re
from datetime import datetime
from ...excel import ExcelDictWriter, ExcelStyle
from ..styles import Style
from ..enums import DataType
from .base import IReportWriter


class ExcelReportWriter(IReportWriter):
    """
    Writes a report in the Excel format.

    This writer expects a bytes stream, so if stream is a file, it must
    be opened in binary mode::

        with open(path, 'wb') as f:
    """
    def __init__(self, definition, stream, close_stream):
        super().__init__(definition, stream, close_stream)
        self.writer = ExcelDictWriter(stream, self.definition.list_fields())
        self.style_cache = {}
        self.format_cache = {d: self._create_excel_number_format(d) for d in DataType}
        self.column_styles = {c.field_name: Style.combine(self.definition.default_style, c.colstyle)
                              for c in self.definition.columns}
        self.column_excel_styles = {f: self._get_excel_style(s)
                                    for f, s in self.column_styles.items()}

        for column in self.definition.columns:
            if column.width is not None:
                self.writer.set_column_style(column.index, width=column.width)

    def writerow(self, rowdict, styledict=None, rowstyle=None):
        styledict = self._resolve_row_styles(styledict, rowstyle)
        self.writer.writerow(rowdict, styledict)

    def freeze_pane(self, col_idx=None, row_idx=None):
        self.writer.freeze_pane(col_idx, row_idx)

    def close(self, exception_was_raised=False):
        if not exception_was_raised:
            self.writer.close()
        super().close(exception_was_raised)

    def _resolve_row_styles(self, styledict, rowstyle):
        if styledict is None and rowstyle is None:
            return self.column_excel_styles
        else:
            styledict = styledict or {}
            return {c.field_name: self._get_excel_style(Style.combine(self.column_styles[c.field_name],
                                                                      rowstyle, styledict.get(c.field_name)))
                    for c in self.definition.columns}

    def _get_excel_style(self, style):
        hash = style.get_hash()
        if hash not in self.style_cache:
            self.style_cache[hash] = self._create_excel_style(style)
        return self.style_cache[hash]

    def _create_excel_style(self, style):
        if style.is_empty():
            return None

        kwargs = style.get_style_dict().copy()
        datatype = kwargs.pop('datatype', None)
        colspan = kwargs.pop('colspan', None)
        if 'align' in kwargs:
            kwargs['align'] = kwargs['align'].value
        if 'valign' in kwargs:
            kwargs['valign'] = kwargs['valign'].value.replace('middle', ExcelStyle.VALIGN_MIDDLE)
        if datatype is not None:
            kwargs['number_format'] = self.format_cache[datatype]

        return ExcelStyle(**kwargs)

    def _create_excel_number_format(self, datatype):
        if datatype in (DataType.CURRENCY, DataType.PERCENTAGE):
            return self.definition.formatter.format(datatype, 0)
        elif datatype == DataType.INT:
            v = self.definition.formatter.format_int(1234)
            return '#,##0' if ',' in v else '0'
        elif datatype == DataType.FLOAT:
            v = self.definition.formatter.format_float(1234.12345)
            head = '#,##0.' if ',' in v else '0.'
            tail = '0' * len(v.split('.')[1])
            return head + tail
        elif datatype == DataType.BOOL:
            n = self.definition.formatter.format_bool(False)
            y = self.definition.formatter.format_bool(True)
            return '&quot;{}&quot;;&quot;{}&quot;;&quot;{}&quot;'.format(y, y, n)
        elif datatype in (DataType.DATE, DataType.DATETIME):
            return self._create_excel_date_format(datatype)
        else:
            return 'General'

    def _create_excel_date_format(self, datatype):
        val = self.definition.formatter.format(datatype, datetime(2022, 4, 5, 7, 8, 9)).lower()
        val = (val.replace('2022', 'yyyy').replace('22', 'yy')
                  .replace('april', 'mmmm').replace('apr', 'mmm')
                  .replace('04', 'mm').replace('4', 'm')
                  .replace('05', 'dd').replace('5', 'd')
                  .replace('07', 'hh').replace('7', 'h')
                  .replace('08', 'mm').replace('8', 'm')
                  .replace('09', 'ss').replace('9', 's'))
        val = re.sub(r'(am)|(pm)|(AM)|(PM)', 'AM/PM', val)
        return val
