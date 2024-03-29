from datetime import datetime
from pyexcelerate import Workbook, Style, Fill, Color, Font, Format, Alignment, Panes
from pyexcelerate.Borders import Borders
from pyexcelerate.Border import Border


class ExcelStyle:
    """
    Created a new style.

    ``number_format`` is an Excel format string, such as ``'yyyy-mm-dd h:mm:ss'``,
    ``'0%'`` etc.

    ``font`` is a string family name.

    ``fontsize`` is an integer point size.

    ``color``, ``bgcolor`` is an integer RGB value (eg. ``0xFF0000`` for red)

    ``align``, ``valign`` are one of the ``HALIGN_`` and ``VALIGN_`` constants.

    All other arguments are boolean.
    """

    HALIGN_LEFT = "left"
    HALIGN_CENTER = "center"
    HALIGN_RIGHT = "right"
    HALIGN_JUSTIFY = "justify"

    VALIGN_TOP = "top"
    VALIGN_MIDDLE = "center"
    VALIGN_BOTTOM = "bottom"

    def __init__(
        self,
        number_format=None,
        font=None,
        fontsize=None,
        bold=None,
        italic=None,
        underline=None,
        strike=None,
        color=None,
        bgcolor=None,
        align=None,
        valign=None,
        wrap_text=None,
        grid_color=None,
        colspan=None,
    ):
        self._styles = locals().copy()
        del self._styles["self"]
        self._excel_style = Style()

        # Number Format
        if number_format is not None:
            self._excel_style.format = Format(number_format)

        # Fonts
        font_kwargs = {}
        if font is not None:
            font_kwargs["family"] = font
        if fontsize is not None:
            font_kwargs["size"] = fontsize
        if bold is not None:
            font_kwargs["bold"] = bold
        if italic is not None:
            font_kwargs["italic"] = italic
        if underline is not None:
            font_kwargs["underline"] = underline
        if strike is not None:
            font_kwargs["strikethrough"] = strike
        if color is not None:
            font_kwargs["color"] = self._to_excel_color(color)

        if len(font_kwargs):
            self._excel_style.font = Font(**font_kwargs)

        # Fill
        if bgcolor is not None:
            self._excel_style.fill = Fill(background=self._to_excel_color(bgcolor))

        # Grid
        if grid_color is not None:
            if isinstance(grid_color, bool) and not grid_color:
                self._excel_style.borders = Borders()
            else:
                border = Border(color=self._to_excel_color(grid_color))
                self._excel_style.borders = Borders(border, border, border, border)

        # Alignment
        align_kwargs = {}
        if align is not None:
            align_kwargs["horizontal"] = align
        if valign is not None:
            align_kwargs["vertical"] = valign
        if wrap_text is not None:
            align_kwargs["wrap_text"] = wrap_text

        if len(align_kwargs):
            self._excel_style.alignment = Alignment(**align_kwargs)

    def __str__(self):
        s = ["ExcelStyle:"]
        for k in sorted(self._styles.keys()):
            v = self._styles[k]
            if v is None:
                continue
            if k in ("color", "bgcolor", "grid_color"):
                v = "0x{:06x}".format(v)
            elif isinstance(v, bool):
                v = "Y" if v else "n"
            s.append("{}={}".format(k.split("_")[0].capitalize(), v))
        return " ".join(s)

    def __repr__(self):
        return str(self)

    @property
    def colspan(self):
        return self._styles["colspan"]

    def copy(self, **kwargs):
        """
        Copy this style, optionally overriding any constructor values given in ``kwargs``.
        """
        kw = self._styles.copy()
        kw.update(kwargs)
        return ExcelStyle(**kw)

    def get_excel_style(self):
        return self._excel_style

    def _to_excel_color(self, color):
        return Color((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)


class ExcelWriter:
    """
    Writes an Excel XLSX file.

    :param filename_or_stream: The path to write the XLSX file or any stream
        to receive the file contents.
    :param str sheet_name: The name of the sheet to write to.
    """

    def __init__(self, filename_or_stream, sheet_name="Sheet1"):
        self._stream = filename_or_stream
        self._workbook = Workbook()

        if sheet_name is not None:
            self._sheet = self._workbook.new_sheet(sheet_name)

        self._default_style = None
        self._rowcount = 0

    @staticmethod
    def content_type():
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.close()

    def add_sheet(self, sheet_name):
        self._sheet = self._workbook.new_sheet(sheet_name)
        self._rowcount = 0

    def num_rows(self):
        return self._rowcount

    def set_default_style(self, style):
        """
        Sets the default style to be used by cells with no specified style.
        """
        self._default_style = style

    def set_column_style(self, index, number_format=None, width=None):
        """
        Sets the width and/or number format of a single column in the sheet.

        NOTE: Seems to be a bug setting the number format for a column to
        a date format.

        :param int index: The 0-based index of the column.
        :param int width: The 'em' widths for the column.
        :param str number_format: The excel number format, eg '0.0%'
        """
        current = self._sheet.get_col_style(index + 1)
        style = {
            "format": current.format,
            "size": current.size,
        }

        if number_format is not None:
            style["format"] = Format(number_format)

        if width is not None:
            style["size"] = width * 2

        self._sheet.set_col_style(index + 1, Style(**style))

    def set_row_style(self, index, number_format=None, height=None):
        """
        Sets the height and/or number format of a single row in the sheet.

        :param int index: The 0-based index of the row.
        :param int height: The 'em' height for the row.
        :param str number_format: The excel number format, eg '0.0%'
        """
        current = self._sheet.get_row_style(index + 1)
        style = {
            "format": current.format,
            "size": current.size,
        }

        if number_format is not None:
            style["format"] = Format(number_format)

        if height is not None:
            style["size"] = height * 2

        self._sheet.set_row_style(index + 1, Style(**style))

    def set_all_column_formats(self, formats):
        """
        Sets the number format of each column in the sheet.

        :param list formats: A list of format strings, or None to skip.
        """
        for i, fmt in enumerate(formats):
            if fmt is not None:
                self.set_column_style(i, number_format=fmt)

    def set_all_column_widths(self, widths):
        """
        Sets the width of each column in the sheet.

        :param list widths: A list of 'em' widths for each column.
        """
        for i, width in enumerate(widths):
            if width is not None:
                self.set_column_style(i, width=width)

    def writerow(self, rowdata, style=None):
        """
        Writes a single row to the Excel sheet.

        :param list rowdata: A list of values for each column in the row.
        :param ExcelStyle style: List of styles for each column, or single style for all columns.
            If not specified uses default style, if set. Can use None in the list to leave
            a cell unstyled.
        """
        self._rowcount += 1
        i = self._rowcount

        if isinstance(style, ExcelStyle):
            merges = [style.colspan] * len(rowdata)
            style = [style.get_excel_style()] * len(rowdata)
        elif style is not None:
            merges = [s.colspan if s is not None else None for s in style]
            style = [s.get_excel_style() if s is not None else None for s in style]
        elif self._default_style is not None:
            merges = ()
            style = [self._default_style.get_excel_style()] * len(rowdata)
        else:
            merges = ()
            style = ()

        for j, val in enumerate(rowdata):
            # Strip tzinfo from datetime objects. They
            # need to be localized before writing.
            if isinstance(val, datetime):
                val = val.replace(tzinfo=None)

            # Coerce bool to int, excel can't format bools
            # You can use this number_format for coerced value:
            # '&quot;Yes&quot;;&quot;Yes&quot;;&quot;No&quot;'
            elif isinstance(val, bool):
                val = 1 if val else 0

            self._sheet.set_cell_value(i, j + 1, val)
            if val is not None and j < len(style) and style[j] is not None:
                self._sheet.set_cell_style(i, j + 1, style[j])

            # Merge any cells to effect "colspan"
            if val is not None and j < len(merges) and merges[j] is not None:
                self._sheet.range((i, j + 1), (i, j + merges[j])).merge()

    def writerows(self, rows):
        """
        Writes a list of row data to the Excel sheet, with default styling.
        """
        for row in rows:
            self.writerow(row)

    def freeze_pane(self, col_idx=None, row_idx=None):
        """
        Freezes the specified column and/or row panes.
        """
        self._sheet.panes = Panes(x=col_idx, y=row_idx, freeze=True)

    def close(self):
        """
        Writes out the Excel data to the file/stream and
        invalidates this instance.
        """
        if isinstance(self._stream, str):
            self._workbook.save(self._stream)
        else:
            self._workbook._save(self._stream)
