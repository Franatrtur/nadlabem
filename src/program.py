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

    def register_variable(self, variable: VariableLexer):
        variables = self.get_variables()
        for var in variables:
            if var.label == variable.label:
                raise Exception(f"Variable {variable.label} already exists: {variable}")

        self.children.insert(0, variable)

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