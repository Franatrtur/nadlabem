from lexer import Lexer
from tokenizer import NameToken, NumberToken, Line, EqualsToken

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
        
        self.var1_name = line.tokens[0].string
        self.literal = line.tokens[2].string
        self.original_line = line

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        return [
            f"MVI A,{self.literal} ;{self.original_line.string} (line {self.original_line.number})",
            f"STA {self.var1_name}"
        ]

"""
x=5;
---
MVI A,<8bit data> - loads constant into register A (or ADI)
STA <target>
"""