from ..lexer import Lexer
from ..tokenizer import NameToken, NumberToken, Line, EqualsToken, PlusToken
from .variable import DefineByteLexer

class AddVarToVarLexer(Lexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return len(line.tokens) == 6 and \
            isinstance(line.tokens[0], NameToken) and \
            isinstance(line.tokens[1], EqualsToken) and \
            isinstance(line.tokens[2], NameToken) and \
            isinstance(line.tokens[3], PlusToken) and \
            isinstance(line.tokens[4], NameToken)

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away
        stack.pop()
        
        self.var1_label = line.tokens[0].string
        self.var2_label = line.tokens[2].string
        self.var3_label = line.tokens[4].string

        self.var1 = DefineByteLexer.create_if_doesnt_exist(self.var1_label, line, self, self.root)
        self.var2 = self.root.get_variable(self.var2_label, line)
        self.var3 = self.root.get_variable(self.var3_label, line)

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        spacing = " " * self.root.config.tabspaces
        return [
            f"{spacing}LDA {self.var2_label} {self.comment}",
            f"{spacing}MOV B,A",
            f"{spacing}LDA {self.var3_label}",
            f"{spacing}ADD B",
            f"{spacing}STA {self.var1_label}"
        ]

"""
x=x+y;
---
LDA <target2>
MOV B,A
LDA <target3>
ADD B
STA <target1>
"""