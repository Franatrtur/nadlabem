from ..tokenizer import Line, NameToken, DefineByteToken, NumberToken, match_token_pattern
from ..config import TranslationConfig
from ..lexer import Lexer
from ..program import VariableLexer

class DefineByteLexer(VariableLexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return match_token_pattern(line, [NameToken, DefineByteToken, NumberToken], ignore_subsequent_tokens=True)

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away (1 line instruction)
        stack.pop()
        
        self.label = line.tokens[0].string
        self.init_value = line.tokens[2].string
        self.synthetic = False

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        spacing = " " * (self.program.config.tabspaces - len(self.label))
        return [f"{self.label}{spacing}DB {self.init_value} {self.map_comment if self.synthetic else ''}"]