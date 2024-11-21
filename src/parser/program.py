from ..tokenizer import Token, NewLineToken, OpenParenToken, CloseParenToken, ArrayBeginToken, ArrayEndToken
from ..errors import SyntaxError
from ..ui import progress_bar
from typing import Type, Union
from .parsing import Parser
from .statement import CodeBlockParser
from ..nodes.node import ProgramNode
from .suggestions import find_suggestion

class ProgramParser(Parser):

    def __init__(self, tokens: list[Token], compiler: Union["Compiler", None] = None):
        self.tokens = tokens
        self.i: int = 0
        self.root = self  # this is the top level parser
        self.parent = None
        self.compiler = compiler
        self.nested: int = 0
        self.children = []
        self.config = compiler.config

    def parse(self) -> ProgramNode:
        program_block = CodeBlockParser(parent=self, force_multiline=True).parse()
        return ProgramNode(program_block.children, parser=self)

    def devour(self, token_type: Type[Token], parser: Parser | None) -> Token:
        if self.is_done:
            raise SyntaxError(f"Unexpected end of input, expected {token_type.__name__} but got nothing", line=self.tokens[self.i].line, parser=parser)

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

            if self.compiler is not None and self.compiler.config.verbose:
                progress_bar("Parsing", self.i, len(self.tokens))

            return token
            
        else:
            raise SyntaxError(f"Expected {token_type.__name__}, but got {self.tokens[self.i]} instead", line=self.tokens[self.i].line, suggestion=find_suggestion(token_type, self.tokens[self.i]))

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