from .tokenizer import Line
from .config import TranslationConfig
from .ui import progress_bar
from .lexer import Lexer
from .lexer import VariableLexer

#TODO: add global registering of variables



class ProgramFrame(Lexer):

    def __init__(self, line: Line, config: TranslationConfig):
        super().__init__(line, None, None)
        self.root = self
        self.config = config

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
        if self.has_variable(variable.label):
            raise Exception(f"Variable {variable.label} already exists: {variable}. Traceback: {traceback}")

        self.children.insert(0, variable)

    def generate_variable(self, preffered_name: str, init_value: int, traceback: Line):
        label_num = 1
        label = f"{preffered_name}{label_num}"
        while self.has_variable(label):
            label_num += 1
            label = f"{preffered_name}{label_num}"
        
        return VariableLexer.create(traceback, self, self, label, init_value)

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