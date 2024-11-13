from ..tokenizer import Token, Line, NewLineToken, CommaToken, NameToken, IntegerLiteralToken
from ..errors import SyntaxError
from ..tree import Node
from typing import Union, Type
from .parse import RecursiveDescentParser
from .nodes import AbstractSyntaxTreeNode as ASTNode


class Parser(Node):

    token: Token

    def __init__(self, parent: Union["Parser", RecursiveDescentParser]):
        super().__init__(parent)
        self.context = self.parent.context
        self.root: RecursiveDescentParser

    def devour(self, token_type: Type[Token]) -> Token:
        return self.root.devour(token_type)

    def look_ahead(self) -> Token:
        return self.root.look_ahead()

    def is_ahead(self, token_type: Type[Token]) -> bool:
        return token_type.match(self.root.look_ahead())

    @property
    def is_done(self) -> bool:
        return self.root.is_done

    @classmethod
    def detect(cls, token: Token) -> bool:
        return cls.token.match(token)

    def parse(self, expect_end: Type[Token] | None = None) -> ASTNode:
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(\"{[child.__str__() for child in self.children]}\")"

