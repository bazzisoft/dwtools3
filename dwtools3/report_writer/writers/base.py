class IReportWriter:
    """
    Interface for all writers that can be used to render
    the report. See the ``OutputType`` enum.

    This class is a context manager and so is meant to be
    used with the ``with`` statement.
    """

    def __init__(self, definition, stream, close_stream):
        self.stream = stream
        self.close_stream = close_stream
        self.definition = definition

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close(exc_type is not None)

    def list_excluded_datatypes(self):
        return ()

    def writeheader(self, styledict=None, rowstyle=None):
        """
        Write out a header row with the column labels or field names.

        :param dict styledict: Optional dict of ``Style`` to apply to the specified columns.
        :param Style rowstyle: Optional ``Style`` to apply to entire row.
        """
        rowdict = {c.field_name: c.label for c in self.definition.columns}
        self.writerow(rowdict, styledict, rowstyle)

    def writerow(self, rowdict, styledict=None, rowstyle=None):
        """
        Write out a row of data.

        :param dict rowdict: Dict of data values for each report column.
        :param dict styledict: Optional dict of ``Style`` to apply to the specified fields.
        :param Style rowstyle: Optional ``Style`` to apply to entire row.
        """
        raise NotImplementedError

    def writerows(self, rowdicts, rowstyle=None):
        """
        Write multiple rows of data, with no or the same styling.
        """
        for rowdict in rowdicts:
            self.writerow(rowdict, rowstyle=rowstyle)

    def freeze_pane(self, col_idx=None, row_idx=None):
        """
        Freezes the specified column and/or row panes if supported.
        """
        pass

    def close(self, exception_was_raised=False):
        """
        Writes out any footer data and closes the writer. Called automatically
        if using the ``with`` statement.
        """
        if self.close_stream:
            self.stream.close()
