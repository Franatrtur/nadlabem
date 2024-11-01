from .tokenizer import Line
from .tree import Tree
from .config import TranslationConfig
from .ui import progress_bar


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

class ProgramFrame(Lexer):

    def __init__(self, config: TranslationConfig):
        super().__init__(None, None)
        self.root = self
        self.config = config

    @staticmethod
    def detect(self, line: Line) -> bool:
        raise "Initial ProgramFrame lexer cannot detect by design"

    def process(self, line: Line, stack: list[Lexer]) -> bool: #vrátí, jestli to spapal
        return False

    def translate(self) -> list[str]:
        translated = []
        for i, child in enumerate(self.children):
            translated.extend(child.translate())

            if self.config.verbose:
                progress_bar("Translating", i+1, len(self.children))

        return translated

    def updateProgress(self, progress: float):
        self.progress = 0