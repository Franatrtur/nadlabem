from tree import Tree
from tokenizer import Line
from lexer import Lexer, InitialLexer


# ------------ LEXERS BEGIN --------------
from ignore import IgnoreLexer, NoLexer

from save_literal_to_var import SaveLiteralToVarLexer
from save_var_to_var import SaveVarToVarLexer

from add_var_to_var import AddVarToVarLexer
from add_literal_to_var import AddLiteralToVarLexer

from sub_literal_from_var import SubLiteralFromVarLexer
from sub_var_from_var import SubVarFromVarLexer

#order matters as priority is used for detection
LEXERS: list[Lexer] = [
    IgnoreLexer,

    SaveLiteralToVarLexer,
    SaveVarToVarLexer,

    AddVarToVarLexer,
    AddLiteralToVarLexer,

    SubLiteralFromVarLexer,
    SubVarFromVarLexer,

    NoLexer
]
# ------------ LEXERS END --------------



def parse(lines: list[Line]) -> Lexer:
    initial_lexer = InitialLexer()
    stack: list[Lexer] = [initial_lexer]

    for line in lines:

        top_lexer = stack[-1]

        if not top_lexer.process(line, stack):
            top_lexer = stack[-1] #reload, as the top lexer might have left

            new_lexer_class = select_lexer_class(line)
            new_lexer = new_lexer_class(top_lexer, top_lexer.root)
            top_lexer.children.append(new_lexer)

            stack.append(new_lexer)

            new_lexer.process(line, stack)

    return initial_lexer


def select_lexer_class(line):
    for lexer in LEXERS:
        if lexer.detect(line):
            return lexer