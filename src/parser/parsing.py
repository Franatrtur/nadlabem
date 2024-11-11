from ..tokenizer import Token, Line, NewLineToken, CommaToken, NameToken, IntegerLiteralToken
from ..errors import SyntaxError
from ..tree import Node
from typing import Union, Type


class Parser(Node):

    token: Token

    def __init__(self, parent: Union["Parser", "RecursiveDescentParser"]):
        super().__init__(parent)
        self.context = self.parent.context
        self.root: "RecursiveDescentParser"

    def eat(self, token_type: Type[Token], skip_newline: bool = False) -> Token:
        return self.root.eat(token_type, skip_newline)

    def look_ahead(self, skip_newline: bool = False) -> Token:
        return self.root.look_ahead(skip_newline)

    def is_ahead(self, token_type: Type[Token], skip_newline: bool = False) -> bool:
        return token_type.match(self.root.look_ahead(skip_newline))

    @classmethod
    def detect(cls, token: Token) -> bool:
        return cls.token.match(token)

    def parse(self, expect_end: Type[Token] | None = None):
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(\"{[child.__str__() for child in self.children]}\")"

