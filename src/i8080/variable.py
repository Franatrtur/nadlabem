from ..tokenizer import Line, NameToken, DefineByteToken, NumberToken, match_token_pattern
from ..config import TranslationConfig
from ..lexer import Lexer
from ..labels import VariableLexer

class DefineByteLexer(VariableLexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return match_token_pattern(line, [NameToken, DefineByteToken, NumberToken])

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away (1 line instruction)
        stack.pop()
        
        self.label = line.tokens[0].string
        self.init_value = line.tokens[2].string
        self.synthetic = False

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        return [f"{self.program.justify_label(self.label, self)}DB {self.init_value} {self.map_comment if self.synthetic else ''}"]