from ..tokenizer import Line, NameToken, DefineByteToken, NumberLiteralToken, match_token_pattern
from ..config import TranslationConfig
from ..lexer import Lexer
from ..labeled import VariableLexer

class DefineByteLexer(VariableLexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return match_token_pattern(line, [NameToken, DefineByteToken, NumberLiteralToken])

    def register(self):
        self.command = "DB"
        self.arguments = [self.init_value]
        super().register()

    def process(self, line: Line, stack: list[Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away (1 line instruction)
        stack.pop()
        
        self.label = line.tokens[0].string
        self.init_value = line.tokens[2].string
        self.synthetic = False
        
        #we are done
        self.register()

        #ano, spapal jsem to já
        return True