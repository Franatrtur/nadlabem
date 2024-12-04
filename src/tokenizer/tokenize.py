import re, ast
from typing import Type, Union
from .symbols import *
from ..tree import Node
from ..errors import SymbolError, NadLabemError
from ..ui import progress_bar


def split_tokens(line_string: str) -> list[str]:
    # Regular expression to match words, numbers, and punctuation, newly also strings and comments
    pattern = r""";.*|>=|==|!=|<=|<<|>>|<<<|>>>|->|=@=|"(?:\\"|[^"])*"|'(?:\\'|[^'])*'|\b\w+\b|[^\w\s]"""
    tokens = re.findall(pattern, line_string)

    return tokens


def tokenize_line(line_string: str, line_number: int | None = None) -> Line:
    token_strings = split_tokens(line_string)
    line = Line(line_string, line_number)

    for token_string in token_strings:

        token: Token = None

        for token_type in TOKEN_DETECTORS:

            if token_type.detect(token_string):
                token = token_type(token_string, line)
                
                if CommentToken is token_type:
                    line.comment = token.string
                else:
                    line.tokens.append(token)
                
                break

        if not token:
            raise SymbolError(f"Unknown token \"{token_string}\"", f"Line {line_number}: \"{line_string}\"")


    if len(line.tokens) > 0:
        line.tokens.append(NewLineToken("\n", line))

    return line


def match_token_pattern(line: Line, token_types: list[Type[Token]], ignore_subsequent_tokens: bool = False) -> bool:

    # First check if we have enough tokens to match the pattern
    # Check if pattern matches for the required token types
    length_match = len(line.tokens) >= len(token_types) if ignore_subsequent_tokens else len(line.tokens) == len(token_types)

    return length_match and all(
        token_types[i].match(line.tokens[i])
        for i in range(len(token_types))
    )


class Tokenizer:

    def __init__(self, compiler: Union["Compiler", None] = None):
        self.compiler = compiler

    def tokenize(self, source_code: str) -> list[Token]:
        tokens: list[Token] = []
        line_number = 1
        lines_str = source_code.splitlines()

        for line in lines_str:
            if self.compiler and self.compiler.config.verbose:
                progress_bar("Tokenizing", line_number, len(lines_str))

            line_tokens = tokenize_line(line, line_number)
            tokens.extend(line_tokens.tokens)
            line_number += 1

        return tokens
        
