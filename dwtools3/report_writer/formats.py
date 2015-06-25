"""
Formatter classes to convert python datatypes into strings.
"""
import datetime


class IFormatter:
    """
    Interface for report cell value formatting.

    Extend this class to suit your needs and pass it to
    ``ReportDefinition.set_formatter()``.
    """
    def format(self, datatype, v):
        """
        Format the value ``v`` for the given ``datatype``.
        """
        try:
            return getattr(self, datatype.value)(v) if datatype is not None else str(v)
        except (AttributeError, TypeError, ValueError):
            return str(v)

    def format_text(self, v):
        return str(v)

    def format_date(self, v):
        raise NotImplementedError

    def format_datetime(self, v):
        raise NotImplementedError

    def format_bool(self, v):
        raise NotImplementedError

    def format_int(self, v):
        raise NotImplementedError

    def format_float(self, v):
        raise NotImplementedError

    def format_percentage(self, v):
        raise NotImplementedError

    def format_currency(self, v):
        raise NotImplementedError


class DefaultFormatter(IFormatter):
    """
    Default report cell value formatting.
    """
    def format_date(self, v):
        return v.strftime('%Y-%m-%d') if isinstance(v, (datetime.date, datetime.datetime)) else str(v)

    def format_datetime(self, v):
        return v.strftime('%Y-%m-%d %H:%M:%S')

    def format_bool(self, v):
        if not isinstance(v, str):
            return 'Y' if v else 'n'
        else:
            raise TypeError('Not a boolean value.')

    def format_int(self, v):
        return format(v, ',')

    def format_float(self, v):
        return format(v, ',.2f')

    def format_percentage(self, v):
        return format(v, '.1%')

    def format_currency(self, v):
        return '${:.2f}'.format(v)
