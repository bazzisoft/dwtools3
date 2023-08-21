from .writer import ExcelWriter


class ExcelDictWriter(ExcelWriter):
    """
    Writes an Excel sheet from a list of dicts & field names.

    :param filename_or_stream: The path to write the XLSX file or any stream
        to receive the file contents.

    :param list field_names: A list of fields to write for each row.
    """

    def __init__(self, filename_or_stream, field_names):
        super().__init__(filename_or_stream)
        self._field_names = tuple(field_names)

    def write_header_row(self, labels=None, style=None):
        """
        Writes a row with field names or labels.

        :param dict labels: If provided, provides a mapping from ``field_names``
            to labels for display in the Excel sheet.

        :param ExcelStyle style: A style to use for the header row, or a dict
            of styles for each field.
        """
        if labels is None:
            labels = {f: f for f in self._field_names}

        self.writerow(labels, style)

    def writerow(self, rowdict, style=None):
        """
        Writes a single row to the Excel sheet.

        :param dict rowdict: A dicts of values for each column in the row.
        :param ExcelStyle style: A dict of styles for each column, or single style for all columns.
            If not specified uses default style.
        """
        assert isinstance(rowdict, dict)

        data = [rowdict.get(f, None) for f in self._field_names]

        if isinstance(style, dict):
            style = [style.get(f) for f in self._field_names]

        super().writerow(data, style)
