import sys

DOT, BEGIN, END, SEMI, ASSIGN, PLUS, MINUS, MUL, DIV, INTEGER, LPAREN, RPAREN, ID, EOF = 'DOT', 'BEGIN', 'END', 'SEMI', 'ASSIGN', 'PLUS', 'MINUS', 'MUL', 'DIV', 'INTEGER', 'LPAREN', 'RPAREN', 'ID', 'EOF'

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(type=self.type, value=repr(self.value))

    def __repr__(self):
        return self.__str__()

RESERVED_KEYWORD = {
    BEGIN: Token(BEGIN, BEGIN),
    END: Token(END, END)
}

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.currentChar = self.text[self.pos]

    def error(self, message='Invalid character'):
        print(self.error)
        sys.exit()

    def advance(self):
        self.pos += 1

        if self.pos > len(self.text) - 1:
            self.currentChar = None
        else:
            self.currentChar = self.text[self.pos]

    def skipWhitespace(self):
        while self.currentChar is not None and self.currentChar.isspace():
            self.advance()

    def integer(self):
        result = ''

        while self.currentChar is not None and self.currentChar.isdigit():
            result += self.currentChar
            self.advance()

        return int(result)

    def _id(self):
        result = ''

        while self.currentChar is not None and self.currentChar.isalpha():
            result += self.currentChar
            self.advance()

        return RESERVED_KEYWORD.get(result, Token(ID, result))

    def peek(self):
        peekPos = self.pos + 1

        if peekPos > len(self.text) - 1:
            return None
        else:
            return self.text[peekPos]

    def getNextToken(self):
        while self.currentChar is not None:
            if self.currentChar.isspace():
                self.skipWhitespace()

                continue

            if self.currentChar.isdigit():
                return Token(INTEGER, self.integer())

            if self.currentChar.isalpha():
                return self._id()

            if self.currentChar == '.':
                self.advance()

                return Token(DOT, '.')

            if self.currentChar == ';':
                self.advance()

                return Token(SEMI, ';')

            if self.currentChar == ':' and self.peek() == '=':
                self.advance()
                self.advance()

                return Token(ASSIGN, ':=')

            if self.currentChar == '+':
                self.advance()

                return Token(PLUS, '+')

            if self.currentChar == '-':
                self.advance()

                return Token(MINUS, '-')

            if self.currentChar == '*':
                self.advance()

                return Token(MUL, '*')

            if self.currentChar == '/':
                self.advance()

                return Token(DIV, '/')

            if self.currentChar == '(':
                self.advance()

                return Token(LPAREN, '(')

            if self.currentChar == ')':
                self.advance()

                return Token(RPAREN, ')')

            self.error

        return Token(EOF, None)

class AST:
    pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Compound(AST):
    def __init__(self):
        self.children = []

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class NoOp(AST):
    pass

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.currentToken = self.lexer.getNextToken()

    def error(self, message='Invalid syntax'):
        print(message)
        sys.exit()

    def eat(self, tokenType):
        if self.currentToken.type == tokenType:
            self.currentToken = self.lexer.getNextToken()
        else:
            self.error()

    def program(self):
        node = self.compoundStatement()
        self.eat(DOT)

        return node

    def compoundStatement(self):
        self.eat(BEGIN)
        node = self.statementList()
        self.eat(END)
        root = Compound()

        for _node in node:
            root.children.append(_node)

        return root

    def statementList(self):
        node = self.statement()
        result = [node]

        while self.currentToken.type == SEMI:
            self.eat(SEMI)
            result.append(self.statement())

        if self.currentToken.type == ID:
            self.error()

        return result

    def statement(self):
        if self.currentToken.type == BEGIN:
            node = self.compoundStatement()
        elif self.currentToken.type == ID:
            node = self.assignmentStatement()
        else:
            node = self.empty()

        return node

    def assignmentStatement(self):
        left = self.variable()
        op = self.currentToken
        self.eat(ASSIGN)
        right = self.expr()

        return Assign(left, op, right)

    def empty(self):
        return NoOp()

    def variable(self):
        token = self.currentToken
        self.eat(ID)

        return Var(token)

    def expr(self):
        node = self.term()

        while self.currentToken.type in [PLUS, MINUS]:
            op = self.currentToken

            if self.currentToken.type == PLUS:
                self.eat(PLUS)
            else:
                self.eat(MINUS)

            node = BinOp(node, op, self.term())

        return node

    def term(self):
        node = self.factor()

        while self.currentToken.type in [MUL, DIV]:
            op = self.currentToken

            if self.currentToken.type == MUL:
                self.eat(MUL)
            else:
                self.eat(DIV)

            node = BinOp(node, op, self.factor())

        return node

    def factor(self):
        if self.currentToken.type == PLUS:
            op = self.currentToken
            self.eat(PLUS)

            return UnaryOp(op, self.factor())

        elif self.currentToken.type == MINUS:
            op = self.currentToken
            self.eat(MINUS)

            return UnaryOp(op, self.factor())

        elif self.currentToken.type == INTEGER:
            token = self.currentToken
            self.eat(INTEGER)

            return Num(token)
        elif self.currentToken.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)

            return node
        else:
            node = self.variable()

            return node

    def parse(self):
        node = self.program()

        if self.currentToken.type != EOF:
            self.error()

        return node

class NodeVisitor:
    def visit(self, node):
        methodName = 'visit' + type(node).__name__
        visitor = getattr(self, methodName, self.genericVisit)

        return visitor(node)

    def genericVisit(self, node):
        raise Exception('No visit{} method'.format(type(node).__name__))

class Interpreter(NodeVisitor):
    GLOBAL_SCOPE = {}
    
    def __init__(self, parser):
        self.parser = parser

    def visitBinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) / self.visit(node.right)

    def visitNum(self, node):
        return node.value

    def visitUnaryOp(self, node):
        op = node.op.type

        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def visitCompound(self, node):
        for child in node.children:
            self.visit(child)

    def visitNoOp(self, node):
        pass

    def visitAssign(self, node):
        varName = node.left.value
        self.GLOBAL_SCOPE[varName] = self.visit(node.right)

    def visitVar(self, node):
        varName = node.value
        val = self.GLOBAL_SCOPE.get(varName)
        
        if val is None:
            raise NameError(repr(varName))
        else:
            return val

    def interpret(self):
        tree = self.parser.parse()

        return self.visit(tree)
