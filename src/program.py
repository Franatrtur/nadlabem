from .tokenizer import Line
from .config import TranslationConfig
from .ui import progress_bar
from .lexer import Lexer
from .labels import VariableLexer
from .errors import LexicalError


class Program(Lexer):

    def __init__(self, line: Line, config: TranslationConfig):
        super().__init__(line, None, None)
        self.root = self
        self.program = self
        self.config = config
        self.labels: set[str] = set()

    def get_variables(self) -> list[VariableLexer]:
        variables = []
        for child in self.children:
            if isinstance(child, VariableLexer):
                variables.append(child)
        return variables

    def has_variable(self, label: str) -> bool:
        variables = self.get_variables()
        for var in variables:
            if var.label == label:
                return True
        return False

    def get_variable(self, label: str, traceback: Line) -> VariableLexer:
        variables = self.get_variables()
        for var in variables:
            if var.label == label:
                return var
        raise Exception(f"Variable {label} is not defined. Traceback: {traceback}")

    def register_variable(self, variable: VariableLexer, traceback: Line):
        if variable.label in self.labels:
            raise Exception(f"Label {variable.label} already exists: {variable}. Traceback: {traceback}")

        self.children.insert(0, variable)

    def generate_label(self, preffered_name: str):
        label_num = 1
        label = f"{preffered_name}{label_num}"
        while label in self.labels:
            label_num += 1
            label = f"{preffered_name}{label_num}"
        self.labels.add(label)
        return label

    def generate_variable(self, preffered_name: str, init_value: int, traceback: Line):
        label = self.generate_label(preffered_name)
        return VariableLexer.create(traceback, self, self, label, init_value)

    @staticmethod
    def detect(self, line: Line) -> bool:
        raise "Initial Program lexer cannot detect by design"

    def process(self, line: Line, stack: list[Lexer]) -> bool: #vrátí, jestli to spapal
        return False

    def translate(self) -> list[str]:
        translated = []
        for i, child in enumerate(self.children):
            translated.extend(child.translate())

            if self.config.verbose:
                progress_bar("Translating", i+1, len(self.children))

        return translated

    def justify_label(self, label: str, lexer: Lexer):
        if len(label) >= self.config.tabspaces:
            raise LexicalError(f"Label {label} too long > {self.config.tabspaces}. {lexer.start_line}")
        spacing = " " * (self.config.tabspaces - len(label))
        return label + spacing