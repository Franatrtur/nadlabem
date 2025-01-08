from ..tokenizer import Token, Line, NewLineToken, CommaToken, NameToken, NumberToken
from ..errors import SyntaxError
from ..tree import Node
from typing import Type
from ..nodes.node import AbstractSyntaxTreeNode as ASTNode
from pathlib import Path


class Parser(Node):

    def __init__(self, parent: "Parser"):
        super().__init__(parent)
        self.parent.children.append(self)
        self.root: "ProgramParser"

    def devour(self, token_type: Type[Token], skip_newline: bool = False) -> Token:
        """Eats desired token type, returns eaten token, throws proper SyntaxError if not found"""
        return self.root.devour(token_type, parser=self, skip_newline=skip_newline)

    def look_ahead(self, skip_newline: bool = False) -> Token:
        return self.root.look_ahead(skip_newline)

    def is_ahead(self, token_type: Type[Token], skip_newline: bool = False) -> bool:
        return token_type.match(self.root.look_ahead(skip_newline))

    @property
    def current_location(self) -> Path:
        return self.root.tokens[self.root.i].line.location

    @property
    def is_done(self) -> bool:
        return self.root.is_done

    def parse(self, expect_end: Type[Token] | None = None) -> ASTNode:
        pass

    def __str__(self):
        return f"{self.__class__.__name__}({', '.join([child.__str__() for child in self.children])})"
    def __repr__(self):
        return str(self)

