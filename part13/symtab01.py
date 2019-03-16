from spi import Lexer, Parser, BuiltinTypeSymbol, VarSymbol


class SymbolTable(object):
    def __init__(self):
        self._symbols = {}

    def __str__(self):
        symtab_header = 'Symbol table contents'
        lines = ['\n', symtab_header, '_' * len(symtab_header)]
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s

    __repr__ = __str__

    def insert(self, symbol):
        print('Insert: %s' % symbol.name)
        self._symbols[symbol.name] = symbol



if __name__ == '__main__':
    text = """
program SymTab1;
   var x, y : integer;

begin

end.
"""
    lexer = Lexer(text)
    parser = Parser(lexer)
    tree = parser.parse()

    symtab = SymbolTable()
    int_type = BuiltinTypeSymbol('INTEGER')
    symtab.insert(int_type)

    var_x_symbol = VarSymbol('x', int_type)
    symtab.insert(var_x_symbol)

    var_y_symbol = VarSymbol('y', int_type)
    symtab.insert(var_y_symbol)
    print(symtab)
