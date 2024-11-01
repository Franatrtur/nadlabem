from lexer import Lexer
from tokenizer import SemicolonToken, Line


class IgnoreLexer(Lexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return len(line.tokens) == 0 or not isinstance(line.tokens[-1], SemicolonToken)

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away
        stack.pop()
        
        self.original_line = line

        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        return [
            self.original_line.string
        ]


#fallback ignore lexer for when all lexers fail
class NoLexer(IgnoreLexer):

    @staticmethod
    def detect(line: Line) -> bool:
        return True
