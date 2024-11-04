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

    def justify_label(self, label: str, lexer: Lexer):
        if len(label) >= self.config.tabspaces:
            raise NameError(f"Label \"{label}\" too long > {self.config.tabspaces} characters", lexer.start_line)
        spacing = " " * (self.config.tabspaces - len(label))
        return label + spacing

    @staticmethod
    def detect(self, line: Line) -> bool:
        raise "Initial Program lexer cannot detect by design"

    def process(self, line: Line, stack: list[Lexer]) -> bool: #vrátí, jestli to spapal
        return False
        
    @property
    def variables(self) -> dict[str, VariableLexer]:
        pass

    def get_by_label(self, label: str, traceback: Line) -> VariableLexer:
        pass

    def get_variable(self, label: str, traceback: Line) -> VariableLexer:
        pass

    def register(self, instruction: DirectiveLexer) -> None:
        pass

    def generate_label(self, preffered_name: str) -> str:
        pass

    def generate_variable(self, parent: Lexer, preffered_name: str, init_value: int | str):
        pass