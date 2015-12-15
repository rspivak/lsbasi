###############################################################################
#  Exercise 2: Infix to LISP style Translator                                 #
###############################################################################
import unittest

from spi import Lexer, Parser, NodeVisitor


class Infix2LispTranslator(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree

    def visit_BinOp(self, node):
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)
        return '({op} {left} {right})'.format(
            left=left_val,
            right=right_val,
            op=node.op.value,
        )

    def visit_Num(self, node):
        return node.value

    def translate(self):
        return self.visit(self.tree)


def infix2lisp(s):
    lexer = Lexer(s)
    parser = Parser(lexer)
    tree = parser.parse()
    translator = Infix2LispTranslator(tree)
    translation = translator.translate()
    return translation


class Infix2LispTestCase(unittest.TestCase):

    def test_1(self):
        self.assertEqual(infix2lisp('1 + 2'), '(+ 1 2)')

    def test_2(self):
        self.assertEqual(infix2lisp('2 * 7'), '(* 2 7)')

    def test_3(self):
        self.assertEqual(infix2lisp('2 * 7 + 3'), '(+ (* 2 7) 3)')

    def test_4(self):
        self.assertEqual(infix2lisp('2 + 3 * 5'), '(+ 2 (* 3 5))')

    def test_5(self):
        self.assertEqual(infix2lisp('7 + 5 * 2 - 3'), '(- (+ 7 (* 5 2)) 3)')

    def test_6(self):
        self.assertEqual(
            infix2lisp('1 + 2 + 3 + 4 + 5'),
            '(+ (+ (+ (+ 1 2) 3) 4) 5)'
        )


if __name__ == '__main__':
    unittest.main()
