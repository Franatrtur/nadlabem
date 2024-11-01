from ..lexer import Lexer
from ..tokenizer import NameToken, NumberToken, Line, EqualsToken
from .variable import DefineByteLexer

class SaveLiteralToVarLexer(Lexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return len(line.tokens) == 4 and \
            isinstance(line.tokens[0], NameToken) and \
            isinstance(line.tokens[1], EqualsToken) and \
            isinstance(line.tokens[2], NumberToken)

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away
        stack.pop()
        
        self.var1_label = line.tokens[0].string
        self.literal = line.tokens[2].string

        self.var1 = DefineByteLexer.create_if_doesnt_exist(self.var1_label, line, self, self.root)

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        spacing = " " * self.root.config.tabspaces
        return [
            f"{spacing}MVI A,{self.literal} {self.comment}",
            f"{spacing}STA {self.var1_label}"
        ]

"""
x=5;
---
MVI A,<8bit data> - loads constant into register A (or ADI)
STA <target>
"""