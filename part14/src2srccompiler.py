# source-to-source compiler

from spi import (
    Lexer,
    Parser,
    NodeVisitor,
    BuiltinTypeSymbol,
    VarSymbol,
    ProcedureSymbol
)


class ScopedSymbolTable(object):
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbols = {}
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

    def _init_builtins(self):
        self.insert(BuiltinTypeSymbol('INTEGER'))
        self.insert(BuiltinTypeSymbol('REAL'))

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in (
            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level),
            ('Enclosing scope',
             self.enclosing_scope.scope_name if self.enclosing_scope else None
            )
        ):
            lines.append('%-15s: %s' % (header_name, header_value))
        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s

    __repr__ = __str__

    def insert(self, symbol):
        self._symbols[symbol.name] = symbol
        # To output subscripts, we get symbols to store a reference
        # to their scope
        symbol.scope = self

    def lookup(self, name, current_scope_only=False):
        # 'symbol' is either an instance of the Symbol class or None
        symbol = self._symbols.get(name)

        if symbol is not None:
            return symbol

        if current_scope_only:
            return None

        # recursively go up the chain and lookup the name
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)


class SourceToSourceCompiler(NodeVisitor):
    def __init__(self):
        self.current_scope = None
        self.output = None

    def visit_Block(self, node):
        results = []
        for declaration in node.declarations:
            result = self.visit(declaration)
            results.append(result)
        results.append('\nbegin')
        result = self.visit(node.compound_statement)
        result = '   ' + result
        results.append(result)
        results.append('end')
        return '\n'.join(results)

    def visit_Program(self, node):
        program_name = node.name
        result_str = 'program %s0;\n' % program_name

        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=self.current_scope, # None
        )
        global_scope._init_builtins()
        self.current_scope = global_scope

        # visit subtree
        result_str += self.visit(node.block)
        result_str += '.'
        result_str += ' {END OF %s}' % program_name
        self.output = result_str

        self.current_scope = self.current_scope.enclosing_scope

    def visit_Compound(self, node):
        results = []
        for child in node.children:
            result = self.visit(child)
            if result is None:
                continue
            results.append(result)
        return '\n'.join(results)

    def visit_NoOp(self, node):
        pass

    def visit_BinOp(self, node):
        t1 = self.visit(node.left)
        t2 = self.visit(node.right)
        return '%s %s %s' % (t1, node.op.value, t2)

    def visit_ProcedureDecl(self, node):
        proc_name = node.proc_name
        proc_symbol = ProcedureSymbol(proc_name)
        self.current_scope.insert(proc_symbol)

        result_str = 'procedure %s%s' % (
            proc_name, self.current_scope.scope_level
        )

        # Scope for parameters and local variables
        procedure_scope = ScopedSymbolTable(
            scope_name=proc_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = procedure_scope

        if node.params:
            result_str += '('

        formal_params = []
        # Insert parameters into the procedure scope
        for param in node.params:
            param_type = self.current_scope.lookup(param.type_node.value)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.insert(var_symbol)
            proc_symbol.params.append(var_symbol)
            scope_level = str(self.current_scope.scope_level)
            formal_params.append(
                '%s : %s' % (param_name + scope_level, param_type.name)
            )

        result_str += '; '.join(formal_params)
        if node.params:
            result_str += ')'
        result_str += ';'
        result_str += '\n'

        result_str += self.visit(node.block_node)
        result_str += '; {END OF %s}' % proc_name

        # indent procedure text
        result_str = '\n'.join('   ' + line for line in result_str.splitlines())

        self.current_scope = self.current_scope.enclosing_scope

        return result_str

    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.current_scope.lookup(type_name)

        # We have all the information we need to create a variable symbol.
        # Create the symbol and insert it into the symbol table.
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)

        # Signal an error if the table alrady has a symbol
        # with the same name
        if self.current_scope.lookup(var_name, current_scope_only=True):
            raise Exception(
                "Error: Duplicate identifier '%s' found" % var_name
            )

        self.current_scope.insert(var_symbol)
        scope_level = str(self.current_scope.scope_level)
        return '   var %s : %s;' % (var_name + scope_level , type_name)

    def visit_Assign(self, node):
        t2 = self.visit(node.right)
        t1 = self.visit(node.left)
        return '%s %s %s;' % (t1, ':=', t2)

    def visit_Var(self, node):
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise Exception(
                "Error: Symbol(identifier) not found '%s'" % var_name
            )
        scope_level = str(var_symbol.scope.scope_level)
        return '<%s:%s>' % (var_name + scope_level, var_symbol.type.name)


if __name__ == '__main__':
    import sys
    text = open(sys.argv[1], 'r').read()

    lexer = Lexer(text)
    parser = Parser(lexer)
    tree = parser.parse()

    source_compiler = SourceToSourceCompiler()
    source_compiler.visit(tree)
    print(source_compiler.output)
