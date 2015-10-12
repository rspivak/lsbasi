import unittest


class LexerTestCase(unittest.TestCase):
    def makeLexer(self, text):
        from calc5 import Lexer
        lexer = Lexer(text)
        return lexer

    def test_lexer_integer(self):
        from calc5 import INTEGER
        lexer = self.makeLexer('234')
        token = lexer.get_next_token()
        self.assertEqual(token.type, INTEGER)
        self.assertEqual(token.value, 234)

    def test_lexer_mul(self):
        from calc5 import MUL
        lexer = self.makeLexer('*')
        token = lexer.get_next_token()
        self.assertEqual(token.type, MUL)
        self.assertEqual(token.value, '*')

    def test_lexer_div(self):
        from calc5 import DIV
        lexer = self.makeLexer(' / ')
        token = lexer.get_next_token()
        self.assertEqual(token.type, DIV)
        self.assertEqual(token.value, '/')

    def test_lexer_plus(self):
        from calc5 import PLUS
        lexer = self.makeLexer('+')
        token = lexer.get_next_token()
        self.assertEqual(token.type, PLUS)
        self.assertEqual(token.value, '+')

    def test_lexer_minus(self):
        from calc5 import MINUS
        lexer = self.makeLexer('-')
        token = lexer.get_next_token()
        self.assertEqual(token.type, MINUS)
        self.assertEqual(token.value, '-')


class InterpreterTestCase(unittest.TestCase):
    def makeInterpreter(self, text):
        from calc5 import Lexer, Interpreter
        lexer = Lexer(text)
        interpreter = Interpreter(lexer)
        return interpreter

    def test_expression1(self):
        interpreter = self.makeInterpreter('3')
        result = interpreter.expr()
        self.assertEqual(result, 3)

    def test_expression2(self):
        interpreter = self.makeInterpreter('2 + 7 * 4')
        result = interpreter.expr()
        self.assertEqual(result, 30)

    def test_expression3(self):
        interpreter = self.makeInterpreter('7 - 8 / 4')
        result = interpreter.expr()
        self.assertEqual(result, 5)

    def test_expression4(self):
        interpreter = self.makeInterpreter('14 + 2 * 3 - 6 / 2')
        result = interpreter.expr()
        self.assertEqual(result, 17)

    def test_expression_invalid_syntax(self):
        interpreter = self.makeInterpreter('10 *')
        with self.assertRaises(Exception):
            interpreter.expr()


if __name__ == '__main__':
    unittest.main()
