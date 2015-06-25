"""
Provides classes define and generate styled reports in multiple formats.


Dependencies
------------
- openpyxl
- PyExcelerate


Usage
-----
NOTE: You should localize any ``datetime`` objects before writing into the reports,
as any timezone info is stripped out before rendering.

::

    from dwtools3 import report_writer as rw

    DATA = [{
        'text': 'Hello world ',
        'date': datetime.date(2015, 4, 3),
        'datetime': datetime.datetime(2015, 11, 21, 15, 43, 21),
        'int': 1234,
        'float': 22567.8911,
        'currency1': 50,
        'currency2': 34.89,
        'percentage': 0.12345,
        'false': False,
        'true': True,
    }]


    class MyReport(rw.ReportDefinition):
        def __init__(self):
            super().__init__()
            self.set_default_style(rw.Style(font='Arial', fontsize=10, color=0x555580, valign=rw.VAlign.TOP))
            self.add_column('text', 'Text', width=20, colstyle=rw.Style(wrap_text=True))
            self.add_column('date', 'Date', colstyle=rw.Style(datatype=rw.DataType.DATE, bgcolor=0xffeeee))
            self.add_column('datetime', 'Date & Time', width=10, colstyle=rw.Style(datatype=rw.DataType.DATETIME))
            self.add_column('int', 'Int', colstyle=rw.Style(datatype=rw.DataType.INT))
            self.add_column('float', 'Float', colstyle=rw.Style(datatype=rw.DataType.FLOAT))
            self.add_column('currency1', 'Currency #1', colstyle=rw.Style(datatype=rw.DataType.CURRENCY))
            self.add_column('currency2', 'Currency #2', colstyle=rw.Style(datatype=rw.DataType.CURRENCY))
            self.add_column('percentage', 'Percentage', colstyle=rw.Style(datatype=rw.DataType.PERCENTAGE))
            self.add_column('false', 'False', colstyle=rw.Style(datatype=rw.DataType.BOOL, align=rw.Align.CENTER))
            self.add_column('true', 'True', colstyle=rw.Style(datatype=rw.DataType.BOOL, valign=rw.VAlign.MIDDLE))


    def generate_report(writer):
        header_style = rw.Style(bold=True, color=0x000000, bgcolor=0xeeeeee)
        cell_style = {'false': rw.Style(font='Courier New', color=0x009000)}

        writer.writeheader(rowstyle=header_style)
        for row in DATA:
            writer.writerow(row, styledict=cell_style)


    with report_def.create_writer('/tmp/report.html', rw.OutputType.HTML_FULL_PAGE) as writer:
        generate_report(writer)

    with report_def.create_writer('/tmp/report.csv', rw.OutputType.CSV) as writer:
        generate_report(writer)

    with report_def.create_writer('/tmp/report.xlsx', rw.OutputType.EXCEL) as writer:
        generate_report(writer)


Members
-------
"""
from .definition import ReportDefinition
from .writers.base import IReportWriter
from .formats import IFormatter, DefaultFormatter
from .styles import Style
from .enums import DataType, Align, VAlign, OutputType


__all__ = [
    'ReportDefinition',
    'IReportWriter',
    'IFormatter', 'DefaultFormatter',
    'Style',
    'DataType', 'Align', 'VAlign', 'OutputType',
]
