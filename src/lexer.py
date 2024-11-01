from tokenizer import Line
from tree import Tree



class Lexer(Tree):

    @staticmethod
    def detect(self, line: Line) -> bool:
        pass

    def process(self, line: Line, stack: list["Lexer"]) -> bool: #vrátí, jestli to spapal
        pass

    # returns a list of string lines
    def translate(self) -> list[str]:
        pass


#TODO: add global registering of variables

class InitialLexer(Lexer):

    def __init__(self):
        super().__init__(None, None)
        self.root = self

    @staticmethod
    def detect(self, line: Line) -> bool:
        raise "Initial lexer cannot detect by design"

    def process(self, line: Line, stack: list[Lexer]) -> bool: #vrátí, jestli to spapal
        return False

    def translate(self) -> list[str]:
        translated = []
        for child in self.children:
            translated.extend(child.translate())
        return translated