from typing import Type

from .tree import Tree
from .tokenizer import Line
from .lexer import Lexer
from .program import Program
from .config import TranslationConfig
from .ui import progress_bar

from .target import TARGETS


def parse(lines: list[Line], config: TranslationConfig) -> Program:

    program = Program(Line("", -1), config)
    
    #currently open lexers
    #lexers are added here, they exit on their own
    stack: list[Lexer] = [program]

    for line in lines:

        if config.verbose:
            progress_bar("Parsing", line.number, len(lines))

        top_lexer = stack[-1]

        if not top_lexer.process(line, stack):
            top_lexer = stack[-1] #reload, as the top lexer might have left

            new_lexer = select_lexer_class(line, config.target_cpu)(
                line, parent=top_lexer, program=program
            )
            top_lexer.children.append(new_lexer)

            stack.append(new_lexer)

            new_lexer.process(line, stack)

    return program


def select_lexer_class(line: Line, target_cpu: str) -> Type[Lexer]:
    lexers = TARGETS[target_cpu].LEXERS

    for lexer_class in lexers:
        if lexer_class.detect(line):
            return lexer_class