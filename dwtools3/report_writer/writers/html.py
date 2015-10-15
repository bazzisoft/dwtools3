import html
import uuid
from .base import IReportWriter


class HTMLReportWriter(IReportWriter):
    """
    Writes a report in HTML format.

    This writer expects a string stream, so if stream is a file, it must
    be opened in text mode::

        with open(path, 'w', encoding='utf-8') as f:
    """
    def __init__(self, definition, stream, closestream, full_page=False):
        super().__init__(definition, stream, closestream)
        self.full_page = full_page
        self.table_id = 'dwrw-' + uuid.uuid4().hex[::3]
        self.rowcount = 0

        if self.full_page:
            self._write_full_page_header()
        self._write_styles()
        self._write_header()

    def writerow(self, rowdict, styledict=None, rowstyle=None):
        output = []
        self.rowcount += 1
        rowid = 'dwrw-' + str(self.rowcount)

        output.append('    <tr class="{}">'.format(rowid))

        if rowstyle:
            output.append('<style type="text/css">')
            output.append('#{} .{} td {{ {} }}'.format(self.table_id, rowid, self._css_for_style(rowstyle)))
            output.append('</style>')

        skip = 0
        for col in self.definition.columns:
            if skip > 0:
                skip -= 1
                continue

            cellstyle = styledict.get(col.field_name) if styledict else None

            colspan = ''
            if cellstyle:
                cs = cellstyle.get_colspan()
                if cs and cs > 1:
                    skip += cs - 1
                    colspan = ' colspan="{}"'.format(cs)

            style = ' style="{}"'.format(self._css_for_style(cellstyle)) if cellstyle else ''
            datatype = self._determine_datatype(cellstyle, rowstyle, col.colstyle)
            value = rowdict.get(col.field_name, '')
            value = self.definition.formatter.format(datatype, value)

            output.append('<td{}{}>{}</td>'.format(colspan, style, html.escape(value).replace('\n', '<br>')))

        output.append('</tr>\n')
        self.stream.write(''.join(output))

    def close(self, exception_was_raised=False):
        if not exception_was_raised:
            self._write_footer()
            if self.full_page:
                self._write_full_page_footer()

        super().close(exception_was_raised)

    def _write_styles(self):
        styles = []

        if self.full_page:
            styles.append('body { font-family: Calibri, Helvetica, Arial, sans-serif; font-size: 11pt; }')

        styles.append('#{} {{ border-collapse: collapse; }}'.format(self.table_id))
        styles.append('#{} td {{ border: 1px solid #ddd; padding: 3px 6px; {} }}'
                      .format(self.table_id, self._css_for_style(self.definition.default_style)))

        for col in self.definition.columns:
            css = self._css_for_style(col.colstyle, col.width)
            styles.append('#{} td:nth-of-type({}) {{ {} }}'.format(self.table_id, col.index + 1, css))

        self.stream.write('''
<style type="text/css">
{}
</style>
'''.format('\n'.join(styles)))

    def _write_header(self):
        self.stream.write('''
<table id="{}">
  <tbody>
'''.format(self.table_id))

    def _write_footer(self):
        self.stream.write('''
  </tbody>
</table>
''')

    def _write_full_page_header(self):
        self.stream.write('''
<!DOCTYPE html>
<html>
<head>
</head>
<body>
''')

    def _write_full_page_footer(self):
        self.stream.write('''
</body>
</html>
''')

    def _determine_datatype(self, cellstyle, rowstyle, colstyle):
        d = self.definition.default_style.get_datatype()
        d = colstyle.get_datatype() or d
        d = (rowstyle and rowstyle.get_datatype()) or d
        d = (cellstyle and cellstyle.get_datatype()) or d
        return d

    def _css_for_style(self, style=None, width=None):
        css = {}
        s = style.get_style_dict() if style is not None else {}

        if width is not None: css['width'] = '{}em'.format(width)
        if s.get('font') is not None: css['font-family'] = s['font']
        if s.get('fontsize') is not None: css['font-size'] = '{}pt'.format(s['fontsize'])
        if s.get('bold') is not None: css['font-weight'] = 'bold' if s['bold'] else 'normal'
        if s.get('italic') is not None: css['font-style'] = 'italic' if s['italic'] else 'normal'
        if s.get('underline') is not None: css['text-decoration'] = 'underline' if s['underline'] else 'none'
        if s.get('strike') is not None: css['text-decoration'] = 'line-through' if s['strike'] else 'none'
        if s.get('color') is not None: css['color'] = '#{:06x}'.format(s['color'])
        if s.get('bgcolor') is not None: css['background-color'] = '#{:06x}'.format(s['bgcolor'])
        if s.get('align') is not None: css['text-align'] = s['align'].value
        if s.get('valign') is not None: css['vertical-align'] = s['valign'].value

        return ' '.join('{}: {};'.format(k, v) for k, v in css.items())
