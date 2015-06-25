from enum import Enum
from .utils import OutputDef

class OutputType(Enum):
    """
    Enum of output data formats that can be written by the report writer.

    The value of each enum is an ``OutputDef`` object with the following attributes:

    ``content_type``, ``extension``, ``is_binary``, ``file_mode``, ``open_kwargs``.
    """
    HTML = OutputDef(content_type='text/html', extension='html', is_binary=False)
    HTML_FULL_PAGE = OutputDef(content_type='text/html', extension='html', is_binary=False)
    CSV = OutputDef(content_type='text/csv', extension='csv', is_binary=False, open_kwargs={'newline': ''})
    EXCEL = OutputDef(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                      extension='xlsx', is_binary=True)


class DataType(Enum):
    """
    Enum of data types understood by the report writer & ``IFormatter``.
    """
    TEXT = 'format_text'
    DATE = 'format_date'
    DATETIME = 'format_datetime'
    BOOL = 'format_bool'
    INT = 'format_int'
    FLOAT = 'format_float'
    PERCENTAGE = 'format_percentage'
    CURRENCY = 'format_currency'


class Align(Enum):
    """
    Enum of horizontal alignment for ``Style``.
    """
    LEFT = 'left'
    CENTER = 'center'
    RIGHT = 'right'
    JUSTIFY = 'justify'


class VAlign(Enum):
    """
    Enum of vertical alignment for ``Style``.
    """
    TOP = 'top'
    MIDDLE = 'middle'
    BOTTOM = 'bottom'
