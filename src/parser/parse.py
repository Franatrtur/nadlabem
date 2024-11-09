from ..tokenizer import Token, Line, match_token_pattern, NewLineToken
from ..errors import SyntaxError
from ..tree import Node


# will extend block class instead
class RecursiveDescentParser(Node):

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.i = 0

    def scan(self, token_type: Type[Token], skip: list[Type[Token]] = [NewLineToken]) -> Token:
        skip_type = Token.any(*skip)
        while skip_type.match(self.tokens[self.i]):
            self.i += 1
        if self.tokens[self.i].match(token_type):
            self.i += 1
            return self.tokens[self.i - 1]
        else:
            raise SyntaxError(f"Expected {token_type}, but got {self.tokens[self.i]} instead", line=self.tokens[self.i].line)

    def look_ahead(self, skip: list[Type[Token]] = [NewLineToken]) -> Token:
        if self.is_done:
            return None
        i = self.i
        while Token.any(*skip).match(self.tokens[i]):
            i += 1
        return self.tokens[i]

    @property
    def is_done(self) -> bool:
        return self.i >= len(self.tokens)