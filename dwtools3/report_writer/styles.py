"""
Style classes to define styling and formatting
for report data.
"""
import enum


class Style:
    """
    Immutable class representing a style that can be applied as a default style,
    column style, row style or cell style.

    Can be (and should be) reused among all elements with the same styling.

    :param DataType datatype: The type of the data for formatting with ``IFormatter``.
    :param int colspan: How many columns to span (only relvant for cell styles).
    :param str font: The font family name.
    :param int fontsize: The font size in points.
    :param bool bold: Use boldface.
    :param bool italic: Use italics.
    :param bool underline: Use underlining.
    :param bool strike: Use strikeout.
    :param int color: 24-bit RGB font color, such as ``0xFF8022``.
    :param int bgcolor: 24-bit RGB background color, such as ``0xFF8022``.
    :param Align align: Horizontal alignment.
    :param VAlign valign: Vertical alignment.
    :param bool wrap_text: Whether text should wrap into multiple lines or be truncated.
    :param int grid_color: 24-bit RBG font color for cell grid, such as ``0xFF8022``.
    """

    def __init__(
        self,
        datatype=None,
        colspan=None,
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
    ):
        self._styles = {k: v for k, v in locals().items() if k != "self" and v is not None}
        self._hash = None

    def __str__(self):
        s = ["Style:"]
        for k in sorted(self._styles.keys()):
            v = self._styles[k]
            if k in ("color", "bgcolor", "grid_color"):
                v = "0x{:06x}".format(v)
            elif isinstance(v, bool):
                v = "Y" if v else "n"
            elif isinstance(v, enum.Enum):
                v = v.name
            s.append("{}={}".format(k.split("_")[0].capitalize(), v))
        return " ".join(s)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self.get_hash()

    def get_hash(self):
        """
        Returns a unique hash for the combination of styles represented
        by the instance.
        """
        if self._hash is None:
            self._hash = hash(frozenset(self._styles.items()))
        return self._hash

    def get_datatype(self):
        """
        Returns the datatype set in this style, or ``None``.
        """
        return self._styles.get("datatype")

    def get_colspan(self):
        """
        Returns the colspan set in this style, or ``None``.
        """
        return self._styles.get("colspan")

    def get_style_dict(self):
        """
        Returns a dict of all styles set in the instance.

        DO NOT MODIFY!
        """
        return self._styles

    def is_empty(self):
        """
        Returns ``True`` if there are not style elements defined in
        this instance.
        """
        return len(self._styles) == 0

    def copy(self, **kwargs):
        """
        Make a copy of this style, altering any settings given in kwargs.
        """
        kw = self._styles.copy()
        kw.update(kwargs)
        return Style(**kw)

    @staticmethod
    def combine(*args):
        """
        Combine two or more styles into a new instance, where later settings
        override earlier ones.
        """
        kw = {}
        for style in args:
            if style is not None and not style.is_empty():
                kw.update(style._styles)
        return Style(**kw)
