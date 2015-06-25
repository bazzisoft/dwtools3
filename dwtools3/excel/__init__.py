"""
Provides classes to read and write Excel spreadsheets.


Dependencies
------------
- openpyxl
- PyExcelerate


Usage
-----
::

    DATA = ['Hello world', 0.12345, datetime.date(2015, 4, 3), datetime.datetime(2015, 11, 21, 15, 43, 21),
            1234, 567.8911, 50, 34.89, False, True]

    with open('/tmp/out.xlsx', 'wb') as f:
        with ExcelWriter(f) as writer:
            writer.set_default_style(ExcelStyle(font='Courier New', wrap_text=True))
            writer.set_column_style(2, width=20, number_format='mm/dd/yy')
            writer.writerow(DATA, style=ExcelStyle(bold=True))
            writer.writerow(DATA, style=[None,
                                         ExcelStyle(font='Arial', color=0x00FF00, bgcolor=0xFFcccc, fontsize=17, bold=True, italic=True, strike=True, underline=True,
                                                          align=ExcelStyle.HALIGN_RIGHT, valign=ExcelStyle.VALIGN_MIDDLE,
                                                          wrap_text=True),
                                         ExcelStyle(number_format='0.0%')])

    reader = ExcelReader('/tmp/out.xlsx')
    data = reader.read_sheet(0, header_row=False)

    print(reader.list_sheets())
    print(list(data))


Members
-------
"""
from .reader import ExcelReader, ExcelReaderError
from .writer import ExcelWriter, ExcelStyle, ExcelWriterError
from .dictwriter import ExcelDictWriter


__all__ = [
    'ExcelReader', 'ExcelReaderError',
    'ExcelWriter', 'ExcelStyle', 'ExcelReaderError',
    'ExcelDictWriter',
]
