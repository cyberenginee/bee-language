class SymbolTable:
    def __init__(self, parent=None):
        self.symbol = {}
        self.parent = parent

    def get(self, name):
        value = self.symbol.get(name, None)

        if value == None and self.parent:
            return self.parent.get(name)
        
        else:
            return value

    def set(self, name, value):
        self.symbol[name] = value

    def remove(self, name):
        del self.symbol[name]