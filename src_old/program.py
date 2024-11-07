from .tokenizer import Line
from .config import TranslationConfig
from .ui import progress_bar
from .lexer import Lexer
from .labeled import VariableLexer, DirectiveLexer
from .errors import NameError


class Program(Lexer):

    def __init__(self, config: TranslationConfig):
        super().__init__(Line("", -1), None)
        self.root = self
        self.program = self
        self.config = config

    @staticmethod
    def detect(self, line: Line) -> bool:
        raise "Initial Program lexer cannot detect by design"

    def process(self, line: Line, stack: list[Lexer]) -> bool: #vrátí, jestli to spapal
        return False