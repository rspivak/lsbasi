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
        self.value = value

class Compound(AST):
    def __init__(self):
        self.children = children

class Asign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = value

class NoOp(AST):
    pass
