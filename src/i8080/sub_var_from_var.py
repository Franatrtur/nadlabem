from ..lexer import Lexer
from ..tokenizer import NameToken, NumberToken, Line, EqualsToken, MinusToken, match_token_pattern
from .variable import DefineByteLexer

class SubVarFromVarLexer(Lexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return match_token_pattern(line, [NameToken, EqualsToken, NameToken, MinusToken, NameToken])

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away
        stack.pop()
        
        self.var1_label = line.tokens[0].string
        self.var2_label = line.tokens[2].string
        self.var3_label = line.tokens[4].string

        #assert variables exist
        self.var2 = self.program.get_variable(self.var2_label, line)
        self.var3 = self.program.get_variable(self.var3_label, line)
        self.var1 = DefineByteLexer.create_if_doesnt_exist(self.var1_label, line, self, self.program)

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        spacing = " " * self.program.config.tabspaces
        return [
            f"{spacing}LDA {self.var2_label} {self.map_comment}",
            f"{spacing}MOV B,A",
            f"{spacing}LDA {self.var3_label}",
            f"{spacing}CMA",
            f"{spacing}INR A",
            f"{spacing}ADD B",
            f"{spacing}STA {self.var1_label}"
        ]

"""
x=x-y;
---
LDA <target2>
MOV B,A
LDA <target3>
CMA
INR A
ADD B
STA <target1>
"""