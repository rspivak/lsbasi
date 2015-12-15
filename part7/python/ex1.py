###############################################################################
#  Exercise 1: Infix to Postfix Translator                                    #
###############################################################################
import unittest

from spi import Lexer, Parser, NodeVisitor


class Infix2PostfixTranslator(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree

    def visit_BinOp(self, node):
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)
        return '{left} {right} {op}'.format(
            left=left_val,
            right=right_val,
            op=node.op.value,
        )

    def visit_Num(self, node):
        return node.value

    def translate(self):
        return self.visit(self.tree)


def infix2postfix(s):
    lexer = Lexer(s)
    parser = Parser(lexer)
    tree = parser.parse()
    translator = Infix2PostfixTranslator(tree)
    translation = translator.translate()
    return translation


class Infix2PostfixTestCase(unittest.TestCase):

    def test_1(self):
        self.assertEqual(infix2postfix('2 + 3'), '2 3 +')

    def test_2(self):
        self.assertEqual(infix2postfix('2 + 3 * 5'), '2 3 5 * +')

    def test_3(self):
        self.assertEqual(
            infix2postfix('5 + ((1 + 2) * 4) - 3'),
            '5 1 2 + 4 * + 3 -',
        )

    def test_4(self):
        self.assertEqual(
            infix2postfix('(5 + 3) * 12 / 3'),
            '5 3 + 12 * 3 /',
        )


if __name__ == '__main__':
    unittest.main()
