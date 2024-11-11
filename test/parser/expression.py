import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.parser.parse import RecursiveDescentParser
from src.parser.expression import ExpressionParser

from src.tokenizer.tokenize import split_tokens, tokenize_line


class TestParser(unittest.TestCase):

    def setUp(self):
        self.tokens = tokenize_line(input("Expression:")).tokens
        self.parser = RecursiveDescentParser(self.tokens)

    def test_parse(self):
        self.expression_parser = ExpressionParser(self.parser)
        tree = self.expression_parser.parse()
        print(tree)


if __name__ == "__main__":
    unittest.main()