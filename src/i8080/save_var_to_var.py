from ..lexer import Lexer
from ..tokenizer import NameToken, NumberToken, Line, EqualsToken, SemicolonToken
from .variable import DefineByteLexer

class SaveVarToVarLexer(Lexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return len(line.tokens) == 4 and \
            isinstance(line.tokens[0], NameToken) and \
            isinstance(line.tokens[1], EqualsToken) and \
            isinstance(line.tokens[2], NameToken)

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away
        stack.pop()
        
        self.var1_label = line.tokens[0].string
        self.var2_label = line.tokens[2].string

        self.var2 = self.root.get_variable(self.var2_label, line)
        self.var1 = DefineByteLexer.create_if_doesnt_exist(self.var1_label, line, self, self.root)

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        spacing = " " * self.root.config.tabspaces
        return [
            f"{spacing}LDA {self.var2_label} {self.comment}",
            f"{spacing}STA {self.var1_label}"
        ]

"""
x=y;
---
LDA <target>
STA <target>
"""