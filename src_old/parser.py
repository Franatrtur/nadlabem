from typing import Type

from .tree import Node
from .tokenizer import Line
from .lexer import Lexer
from .program import Program
from .config import TranslationConfig
from .ui import progress_bar
from .errors import ParsingError, NameError, SyntaxError, NadLabemError

from .target import TARGETS


def parse(lines: list[Line], config: TranslationConfig) -> Program:

    target = TARGETS[config.target_cpu]

    program = target.PROGRAM(config)
    
    #currently open lexers
    #lexers are added here, they exit on their own
    stack: list[Lexer] = [program]

    for line in lines:

        if config.verbose:
            progress_bar("Parsing", line.number, len(lines))

        top_lexer = stack[-1]

        try:

            if not top_lexer.process(line, stack):
                top_lexer = stack[-1] #reload, as the top lexer might have left

                new_lexer = select_lexer_class(line, target.LEXERS)(
                    line, parent=top_lexer
                )
                top_lexer.add_child(new_lexer)

                stack.append(new_lexer)

                new_lexer.process(line, stack)

        except NadLabemError as e:
            print()
            if isinstance(e, NadLabemError):
                raise e
            else:
                raise ParsingError("Unexpected" + str(e), line)


    if len(stack) != 1:
        raise SyntaxError(f"Expected an end to context {stack[-1].__class__.__name__}", stack[-1].start_line, suggestion="Perhaps you forgot a \"}\" ?")

    return program


def select_lexer_class(line: Line, lexers: list[Type[Lexer]]) -> Type[Lexer]:
    for lexer_class in lexers:
        if lexer_class.detect(line):
            return lexer_class
    raise SyntaxError("Unknown syntax", line)