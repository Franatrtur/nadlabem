from ..lexer import Lexer
from .variable import DefineByteLexer
from ..tokenizer import NameToken, NumberToken, Line, EqualsToken, PlusToken, match_token_pattern

class AddLiteralToVarLexer(Lexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return match_token_pattern(line, [NameToken, EqualsToken, NameToken, PlusToken, NumberToken]) or \
            match_token_pattern(line, [NameToken, EqualsToken, NumberToken, PlusToken, NameToken])

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #one line instruction (exit right away)
        stack.pop()
        
        self.var1_label = line.tokens[0].string

        if NameToken.match(line.tokens[2]):
            name_token_index = 2
            literal_token_index = 4
        else:
            name_token_index = 4
            literal_token_index = 2

        self.var2_label = line.tokens[name_token_index].string
        self.literal = line.tokens[literal_token_index].string

        #assert second variable exists
        self.var2 = self.program.get_variable(self.var2_label, line)
        self.var1 = DefineByteLexer.create_if_doesnt_exist(self.var1_label, line, self, self.program)

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        spacing = " " * self.program.config.tabspaces

        return [
            f"{spacing}LDA {self.var2_label} {self.map_comment}",
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