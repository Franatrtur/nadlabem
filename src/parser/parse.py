from ..tokenizer import Token, Line, match_token_pattern, NewLineToken
from ..errors import SyntaxError
from ..tree import Node
from ..ui import progress_bar
from .scope import Context
from typing import Type


# will extend block class instead
class RecursiveDescentParser(Node):

    def __init__(self, tokens: list[Token], compiler: "Compiler"):
        self.tokens = tokens
        self.i: int = 0
        self.root = self
        self.parent = None
        self.context = Context(self, parent=None)
        self.compiler = compiler

    def eat(self, token_type: Type[Token], skip_newline: bool = False) -> Token:
        if self.is_done:
            raise SyntaxError("Unexpected end of input", line=self.tokens[self.i].line)

        while skip_newline and NewLineToken.match(self.tokens[self.i]):
            self.i += 1
            if self.is_done:
                raise SyntaxError("Unexpected end of multiline input", line=self.tokens[self.i - 1].line)

        if token_type.match(self.tokens[self.i]):
            self.i += 1

            if self.compiler.config.verbose:
                progress_bar("Parsing", self.i, len(self.tokens))

            return self.tokens[self.i - 1]
            
        else:
            raise SyntaxError(f"Expected {token_type.__name__}, but got {self.tokens[self.i]} instead", line=self.tokens[self.i].line)

    def look_ahead(self, skip_newline: bool = False) -> Token:
        if self.is_done:
            return None
        i = self.i
        while skip_newline and NewLineToken.match(self.tokens[i]):
            i += 1
            if i >= len(self.tokens):
                return None
        return self.tokens[i]

    @property
    def is_done(self) -> bool:
        return self.i >= len(self.tokens)