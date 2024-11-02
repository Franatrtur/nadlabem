from .tokenizer import Line
from .config import TranslationConfig
from .ui import progress_bar
from .lexer import Lexer


class VariableLexer(Lexer):

    @classmethod
    def create(cls, line: Line, parent: Lexer, program: Lexer, label: str, init_value: int) -> "VariableLexer":
        var = cls(line, parent, program)

        var.label = label
        var.init_value = init_value
        var.synthetic = True

        #attach to program
        program.register_variable(var, line)

        return var

    @classmethod
    def create_if_doesnt_exist(cls, label: str, line: Line, parent: Lexer, program: "Program") -> "VariableLexer":
        if not program.has_variable(label):
            return cls.create(line, parent, program, label, 0)
        else:
            return program.get_variable(label, line)

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        raise "Abstract class"


class Program(Lexer):

    def __init__(self, line: Line, config: TranslationConfig):
        super().__init__(line, None, None)
        self.root = self
        self.program = program
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