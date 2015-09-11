import unittest


class ParserTestCase(unittest.TestCase):
    def makeParser(self, text):
        from parser import Lexer, Parser
        lexer = Lexer(text)
        parser = Parser(lexer)
        return parser

    def test_expression1(self):
        parser = self.makeParser('7')
        parser.parse()

    def test_expression2(self):
        parser = self.makeParser('7 * 4 / 2')
        parser.parse()

    def test_expression3(self):
        parser = self.makeParser('7 * 4 / 2 * 3')
        parser.parse()

    def test_expression4(self):
        parser = self.makeParser('10 * 4  * 2 * 3 / 8')
        parser.parse()

    def test_expression_invalid_syntax(self):
        parser = self.makeParser('10 *')
        with self.assertRaises(Exception):
            parser.parse()


if __name__ == '__main__':
    unittest.main()
