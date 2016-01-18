import unittest


class LexerTestCase(unittest.TestCase):
    def makeLexer(self, text):
        from spi import Lexer
        lexer = Lexer(text)
        return lexer

    def test_lexer_integer(self):
        from spi import INTEGER
        lexer = self.makeLexer('234')
        token = lexer.get_next_token()
        self.assertEqual(token.type, INTEGER)
        self.assertEqual(token.value, 234)

    def test_lexer_mul(self):
        from spi import MUL
        lexer = self.makeLexer('*')
        token = lexer.get_next_token()
        self.assertEqual(token.type, MUL)
        self.assertEqual(token.value, '*')

    def test_lexer_div(self):
        from spi import DIV
        lexer = self.makeLexer(' / ')
        token = lexer.get_next_token()
        self.assertEqual(token.type, DIV)
        self.assertEqual(token.value, '/')

    def test_lexer_plus(self):
        from spi import PLUS
        lexer = self.makeLexer('+')
        token = lexer.get_next_token()
        self.assertEqual(token.type, PLUS)
        self.assertEqual(token.value, '+')

    def test_lexer_minus(self):
        from spi import MINUS
        lexer = self.makeLexer('-')
        token = lexer.get_next_token()
        self.assertEqual(token.type, MINUS)
        self.assertEqual(token.value, '-')

    def test_lexer_lparen(self):
        from spi import LPAREN
        lexer = self.makeLexer('(')
        token = lexer.get_next_token()
        self.assertEqual(token.type, LPAREN)
        self.assertEqual(token.value, '(')

    def test_lexer_rparen(self):
        from spi import RPAREN
        lexer = self.makeLexer(')')
        token = lexer.get_next_token()
        self.assertEqual(token.type, RPAREN)
        self.assertEqual(token.value, ')')


class InterpreterTestCase(unittest.TestCase):
    def makeInterpreter(self, text):
        from spi import Lexer, Parser, Interpreter
        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        return interpreter

    def test_expression1(self):
        interpreter = self.makeInterpreter('3')
        result = interpreter.interpret()
        self.assertEqual(result, 3)

    def test_expression2(self):
        interpreter = self.makeInterpreter('2 + 7 * 4')
        result = interpreter.interpret()
        self.assertEqual(result, 30)

    def test_expression3(self):
        interpreter = self.makeInterpreter('7 - 8 / 4')
        result = interpreter.interpret()
        self.assertEqual(result, 5)

    def test_expression4(self):
        interpreter = self.makeInterpreter('14 + 2 * 3 - 6 / 2')
        result = interpreter.interpret()
        self.assertEqual(result, 17)

    def test_expression5(self):
        interpreter = self.makeInterpreter('7 + 3 * (10 / (12 / (3 + 1) - 1))')
        result = interpreter.interpret()
        self.assertEqual(result, 22)

    def test_expression6(self):
        interpreter = self.makeInterpreter(
            '7 + 3 * (10 / (12 / (3 + 1) - 1)) / (2 + 3) - 5 - 3 + (8)'
        )
        result = interpreter.interpret()
        self.assertEqual(result, 10)

    def test_expression7(self):
        interpreter = self.makeInterpreter('7 + (((3 + 2)))')
        result = interpreter.interpret()
        self.assertEqual(result, 12)

    def test_expression8(self):
        interpreter = self.makeInterpreter('- 3')
        result = interpreter.interpret()
        self.assertEqual(result, -3)

    def test_expression9(self):
        interpreter = self.makeInterpreter('+ 3')
        result = interpreter.interpret()
        self.assertEqual(result, 3)

    def test_expression10(self):
        interpreter = self.makeInterpreter('5 - - - + - 3')
        result = interpreter.interpret()
        self.assertEqual(result, 8)

    def test_expression11(self):
        interpreter = self.makeInterpreter('5 - - - + - (3 + 4) - +2')
        result = interpreter.interpret()
        self.assertEqual(result, 10)

    def test_no_expression(self):
        interpreter = self.makeInterpreter('   ')
        result = interpreter.interpret()
        self.assertEqual(result, '')

    def test_expression_invalid_syntax1(self):
        interpreter = self.makeInterpreter('10 *')
        with self.assertRaises(Exception):
            interpreter.interpret()

    def test_expression_invalid_syntax2(self):
        interpreter = self.makeInterpreter('1 (1 + 2)')
        with self.assertRaises(Exception):
            interpreter.interpret()


if __name__ == '__main__':
    unittest.main()
