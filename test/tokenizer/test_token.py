import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tokenizer.token import Line, Token

class TestToken(unittest.TestCase):

    def setUp(self):
        self.line = Line("example line", 1)

    def test_token_initialization(self):
        token = Token("sample", self.line)
        self.assertEqual(token.string, "sample")
        self.assertEqual(token.line, self.line)

    def test_token_str_representation(self):
        token = Token("sample", self.line)
        self.assertEqual(str(token), 'Token("sample")')

    def test_literal_creation_and_detection(self):
        MyToken = Token.literal("test", "MyToken")
        self.assertTrue(MyToken.detect("test"))
        self.assertTrue(MyToken.detect("TEST"))  # Case insensitive
        self.assertFalse(MyToken.detect("other"))

    def test_match(self):
        MyToken = Token.literal("match", "MyToken")
        token_instance = MyToken("match", self.line)
        self.assertTrue(MyToken.match(token_instance))
        self.assertTrue(Token.match(token_instance))

    def test_any_combined_token_detection(self):
        AlphaToken = Token.literal("alpha", "AlphaToken")
        BetaToken = Token.literal("beta", "BetaToken")
        CombinedToken = Token.any(AlphaToken, BetaToken, class_name="CombinedToken")
        
        self.assertTrue(CombinedToken.detect("alpha"))
        self.assertTrue(CombinedToken.detect("beta"))
        self.assertFalse(CombinedToken.detect("gamma"))

    def test_any_combined_token_match(self):
        AlphaToken = Token.literal("alpha", "AlphaToken")
        BetaToken = Token.literal("beta", "BetaToken")
        CombinedToken = Token.any(AlphaToken, BetaToken, class_name="CombinedToken")
        
        alpha_instance = AlphaToken("alpha", self.line)
        beta_instance = BetaToken("beta", self.line)
        self.assertTrue(CombinedToken.match(alpha_instance))
        self.assertTrue(CombinedToken.match(beta_instance))

class TestLine(unittest.TestCase):

    def test_line_initialization(self):
        line = Line("sample line", 5)
        self.assertEqual(line.string, "sample line")
        self.assertEqual(line.number, 5)
        self.assertEqual(line.tokens, [])
        self.assertEqual(line.comment, "")

    def test_line_str_representation(self):
        line = Line("sample line", 5)
        token = Token("token", line)
        line.tokens.append(token)
        self.assertEqual(str(line), 'Line 5: "sample line" [Token("token")]')

if __name__ == "__main__":
    unittest.main()
