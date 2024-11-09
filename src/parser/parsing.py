from ..tokenizer import Token, Line, NewLineToken, CommaToken, NameToken, IntegerLiteralToken
from ..errors import SyntaxError
from ..tree import Node



class Parser(Node):

    token: Token

    def __init__(self, parent: "Parser" | "RecursiveDescentParser"):
        super().__init__(parent)
        self.context = self.parent.context
        self.parse()
        self.root: "RecursiveDescentParser"

    def scan(self, token_type: Type[Token], skip: list[Type[Token]]) -> Token:
        return self.root.scan(token)

    def look_ahead(self, skip: list[Type[Token]]) -> Token:
        return self.root.look_ahead(skip)

    def will_scan(self, token_type: Type[Token], skip: list[Type[Token]]) -> bool:
        return token_type.match(self.look_ahead(skip))

    @classmethod
    def detect(cls, token: Token) -> bool:
        return cls.token.match(token)

    def parse(self, expect_end: Type[Token] | None = None):
        pass


class 