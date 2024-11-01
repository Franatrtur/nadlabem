from ..tokenizer import Line, NameToken, DefineByteToken, NumberToken, match_token_pattern
from ..config import TranslationConfig
from ..lexer import Lexer, VariableLexer

class DefineByteLexer(VariableLexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return match_token_pattern(line, [NameToken, DefineByteToken, NumberToken], ignore_subsequent_tokens=True)
        
        len(line.tokens) >= 3 and \
            isinstance(line.tokens[0], NameToken) and \
            DefineByteToken.match(line.tokens[1]) and \
            isinstance(line.tokens[2], NumberToken)
            #DefineByteToken.is_type(line.tokens[1]) and \
            #isinstance(line.tokens[1], DefineByteToken) and \

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away
        stack.pop()
        
        self.label = line.tokens[0].string
        self.init_value = line.tokens[2].string
        self.synthetic = False

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        spacing = " " * (self.root.config.tabspaces - len(self.label))
        return [f"{self.label}{spacing}DB {self.init_value} {self.comment if self.synthetic else ''}"]