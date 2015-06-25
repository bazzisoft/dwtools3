

class ColumnDef:
    def __init__(self, index, field_name, label=None, width=None, colstyle=None):
        self.index = index
        self.field_name = field_name
        self.label = label or field_name
        self.width = width
        self.colstyle = colstyle
