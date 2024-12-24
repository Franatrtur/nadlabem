from ..tokenizer import Token, NewLineToken, OpenParenToken, CloseParenToken, ArrayBeginToken, ArrayEndToken, StringLiteralToken
from ..errors import SyntaxError, NadLabemError
from ..ui import progress_bar
from typing import Type
from ..config import CompilationConfig
from .parsing import Parser
from .statement import CodeBlockParser
from ..nodes.node import ProgramNode
from .suggestions import find_suggestion
from .dependency import Dependency
from pathlib import Path
from ..tokenizer import Tokenizer

class ProgramParser(Parser):

    def __init__(self, tokens: list[Token], config: CompilationConfig):
        self.tokens = tokens
        self.i: int = 0
        self.root = self  # this is the top level parser
        self.parent = None
        self.nested: int = 0
        self.children = []
        self.config: CompilationConfig = config

        self.dependencies: dict[Path, Dependency] = {
            self.config.location: Dependency(self.config.location, parent=None)
        }

    def parse(self) -> ProgramNode:
        program_block = CodeBlockParser(parent=self, force_multiline=True).parse()
        return ProgramNode(program_block.children, parser=self)

    def devour(self, token_type: Type[Token], parser: Parser | None) -> Token:
        if self.is_done:
            raise SyntaxError(f"Unexpected end of input, expected {token_type.__name__} but got nothing", line=self.tokens[self.i - 1].line, parser=parser)

        skip_newline = self.nested > 0

        while skip_newline and NewLineToken.match(self.tokens[self.i]):
            self.i += 1
            if self.is_done:
                raise SyntaxError(f"Unexpected end of multiline input, expected {token_type.__name__} but got nothing", line=self.tokens[self.i - 1].line, parser=parser)

        token = self.tokens[self.i]
        token.parsed_by = parser

        if Token.any(OpenParenToken, ArrayBeginToken).match(token):
            self.nested += 1
        elif Token.any(CloseParenToken, ArrayEndToken).match(token):
            self.nested -= 1

        if token_type.match(self.tokens[self.i]):
            self.i += 1

            if self.config.verbose:
                progress_bar("Parsing", self.i, len(self.tokens))

            return token
            
        else:
            raise SyntaxError(f"Expected {token_type.__name__}, but got {self.tokens[self.i]} instead", line=self.tokens[self.i].line, parser=parser, suggestion=find_suggestion(token_type, self.tokens[self.i], parser))

    def look_ahead(self) -> Token:

        skip_newline = self.nested > 0

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

    def inject(self, tokens: list[Token], next_line: bool) -> None:
        offset = 1 if next_line else 0
        self.tokens = self.tokens[:(self.i + offset)] + tokens + self.tokens[(self.i + offset):]