from ..lexer import Lexer
from ..tokenizer import NameToken, NumberToken, Line, EqualsToken, MinusToken, SemicolonToken, match_token_pattern
from .variable import DefineByteLexer

class SaveLiteralToVarLexer(Lexer):

    @staticmethod
    def detect(line: Line) -> bool:
        #handle negative literals too
        return  match_token_pattern(line, [NameToken, EqualsToken, NumberToken, SemicolonToken]) or \
                match_token_pattern(line, [NameToken, EqualsToken, MinusToken, NumberToken, SemicolonToken])

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #one line instruction (exit right away)
        stack.pop()

        self.var1_label = line.tokens[0].string

        if MinusToken.match(line.tokens[2]):
            # make a two´s complement sign inversion
            self.literal_val = ((line.tokens[3].value ^ 0xFF) + 1) & 0xFF
        else:
            self.literal_val = line.tokens[2].value

        self.var1 = DefineByteLexer.create_if_doesnt_exist(self.var1_label, line, self, self.program)

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        spacing = " " * self.program.config.tabspaces
        return [
            f"{spacing}MVI A,{self.literal_val} {self.map_comment}",
            f"{spacing}STA {self.var1_label}"
        ]

"""
x=5;
---
MVI A,<8bit data> - loads constant into register A (or ADI)
STA <target>
"""