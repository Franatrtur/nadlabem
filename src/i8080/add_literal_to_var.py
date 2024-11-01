from ..lexer import Lexer
from ..tokenizer import NameToken, NumberToken, Line, EqualsToken, PlusToken, SemicolonToken, match_token_pattern

class AddLiteralToVarLexer(Lexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return match_token_pattern(line, [NameToken, EqualsToken, NameToken, PlusToken, NumberToken, SemicolonToken])

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away
        stack.pop()
        
        self.var1_label = line.tokens[0].string
        self.var2_label = line.tokens[2].string
        self.literal = line.tokens[4].string

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        spacing = " " * self.root.config.tabspaces

        return [
            f"{spacing}LDA {self.var2_label} {self.comment}",
            f"{spacing}MVI B,{self.literal}",
            f"{spacing}ADD B",
            f"{spacing}STA {self.var1_label}"
        ]

"""
x=y+4;
---
LDA <target2>
MVI B,<8bit data>
ADD B
STA <target1>
"""