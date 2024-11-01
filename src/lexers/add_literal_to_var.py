from ..lexer import Lexer
from ..tokenizer import NameToken, NumberToken, Line, EqualsToken, PlusToken

class AddLiteralToVarLexer(Lexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return len(line.tokens) == 6 and \
            isinstance(line.tokens[0], NameToken) and \
            isinstance(line.tokens[1], EqualsToken) and \
            isinstance(line.tokens[2], NameToken) and \
            isinstance(line.tokens[3], PlusToken) and \
            isinstance(line.tokens[4], NumberToken)

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away
        stack.pop()
        
        self.var1_name = line.tokens[0].string
        self.var2_name = line.tokens[2].string
        self.literal = line.tokens[4].string
        self.original_line = line

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        spacing = " " * self.root.config.tabspaces
        return [
            f"{spacing}LDA {self.var2_name} ;{self.map}",
            f"{spacing}MVI B,{self.literal}",
            f"{spacing}ADD B",
            f"{spacing}STA {self.var1_name}"
        ]

    @property
    def map(self) -> str:
        return f"{self.original_line.string} (line {self.original_line.number})"

    def __str__(self) -> str:
        return self.map

"""
x=y+4;
---
LDA <target2>
MVI B,<8bit data>
ADD B
STA <target1>
"""