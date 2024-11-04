from ..tokenizer import Line
from ..program import Program
from ..config import TranslationConfig
from ..ui import progress_bar
from ..lexer import Lexer
from ..labeled import VariableLexer, DirectiveLexer
from ..errors import NameError


class ProgramI8080(Program):

    def __init__(self, config: TranslationConfig):
        super().__init__(config)
        self.labeled: dict[str, VariableLexer] = {}
        
    @property
    def variables(self) -> dict[str, VariableLexer]:
        return {label: child for label, child in self.labeled.items() if isinstance(child, VariableLexer)}

    def get_by_label(self, label: str, traceback: Line) -> VariableLexer:
        if label not in self.labeled:
            raise NameError(f"Label \"{label}\" not found", traceback)
        return self.labeled[label]

    def get_variable(self, label: str, traceback: Line) -> VariableLexer:
        if label not in self.variables:
            raise NameError(f"Variable \"{label}\" is not defined", traceback)
        return self.variables[label]

    def register(self, instruction: DirectiveLexer) -> None:
        
        if instruction.label in self.labeled.keys():
            raise NameError(f"Label \"{instruction.label}\" already exists", instruction.start_line, other=self.labeled[instruction.label].start_line)
        
        self.labeled[instruction.label] = instruction
        
        if isinstance(instruction, VariableLexer) and instruction not in self.children:
            self.children.insert(0, instruction)

    def generate_label(self, preffered_name: str) -> str:
        label_num = 1
        label = f"{preffered_name}{label_num}"
        while label in self.labeled.keys():
            label_num += 1
            label = f"{preffered_name}{label_num}"
        return label

    def generate_variable(self, parent: Lexer, preffered_name: str, init_value: int | str):
        label = self.generate_label(preffered_name)
        return VariableLexer.create(parent, label, init_value)

    def translate(self) -> list[str]:

        translated = []
        for i, child in enumerate(self.children):
            translated.extend(child.translate())

            if self.config.verbose:
                progress_bar("Translating", i+1, len(self.children))

        #check hlt
        if self.config.verbose and "hlt" not in translated[-1].lower():
            print("\n\33[41m", "Warning", '\033[0m', "missing HLT at the end of the program\n")

        return translated

    def justify_label(self, label: str, lexer: Lexer):
        if len(label) >= self.config.tabspaces:
            raise NameError(f"Label \"{label}\" too long > {self.config.tabspaces} characters", lexer.start_line)
        spacing = " " * (self.config.tabspaces - len(label))
        return label + spacing