

class OutputDef:
    def __init__(self, content_type, extension, is_binary, open_kwargs=None):
        self.content_type = content_type
        self.extension = extension
        self.is_binary = is_binary
        self.file_mode = 'wb' if is_binary else 'w'
        self.open_kwargs = open_kwargs or {}


class ColumnDef:
    def __init__(self, index, field_name, label=None, width=None, colstyle=None):
        self.index = index
        self.field_name = field_name
        self.label = label or field_name
        self.width = width
        self.colstyle = colstyle
