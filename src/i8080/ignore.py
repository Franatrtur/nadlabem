from ..lexer import Lexer
from ..tokenizer import SemicolonToken, Line

#TODO: register db variables
class IgnoreLexer(Lexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return len(line.tokens) == 0 or not isinstance(line.tokens[-1], SemicolonToken)

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away
        stack.pop()
        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        return [
            self.start_line.string
        ]

#TODO: raise error when detect is run as it shouldnt ever run
#fallback ignore lexer for when all lexers fail
class NoLexer(IgnoreLexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return True
