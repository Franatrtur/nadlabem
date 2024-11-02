from ..lexer import Lexer
from ..tokenizer import Line

# AS OF THE CHANGE OF BRANDEJS LANGUAGE GRAMMAR,
# IgnoreLexer class is DEPRACATED and is not included in i8080 lexers
# it is replaced by the NoLexer fallthrough:

class NoLexer(Lexer):

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        #exit right away
        stack.pop()
        #ano, spapal jsem to já
        return True

    def translate(self) -> list[str]:
        return [
            self.start_line.string
        ]

    @staticmethod
    def detect(line: Line) -> bool:
        return True
