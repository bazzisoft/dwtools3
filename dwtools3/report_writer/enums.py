from enum import Enum


class OutputType(Enum):
    """
    Enum of output data formats that can be written by the report writer.
    """
    HTML = 'html'
    HTML_FULL_PAGE = 'html_full_page'
    EXCEL = 'excel'
    CSV = 'csv'


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
