from .tree import Tree
from .tokenizer import Line
from .lexer import Lexer, ProgramFrame
from .config import TranslationConfig

from .lexers import LEXERS


def parse(lines: list[Line], config: TranslationConfig) -> ProgramFrame:
    initial_lexer = ProgramFrame(config)
    stack: list[Lexer] = [initial_lexer]

    for line in lines:

        top_lexer = stack[-1]

        if not top_lexer.process(line, stack):
            top_lexer = stack[-1] #reload, as the top lexer might have left

            new_lexer = select_lexer_class(line)(top_lexer, top_lexer.root)
            top_lexer.children.append(new_lexer)

            stack.append(new_lexer)

            new_lexer.process(line, stack)

    return initial_lexer


def select_lexer_class(line: Line) -> Lexer:
    for lexer in LEXERS:
        if lexer.detect(line):
            return lexer