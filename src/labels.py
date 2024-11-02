from .tokenizer import Line
from .config import TranslationConfig
from .ui import progress_bar
from .lexer import Lexer
from .errors import TranslationError


class InstructionLexer(Lexer):

    @classmethod
    def create(cls, line: Line, parent: Lexer, program: Lexer, label: str, command: str, arguments: list[str]) -> "AssemblyLexer":
        instruction = cls(line, parent, program)

        instruction.label = label
        instruction.command = command
        instruction.arguments = arguments
        instruction.synthetic = True

        #attach to program
        program.register_label(label)

        return instruction

    @classmethod
    def create_if_doesnt_exist(cls, label: str, line: Line, parent: Lexer, program: "Program") -> "AssemblyLexer":
        if not program.has_variable(label):
            return cls.create(line, parent, program, label, 0)
        else:
            return program.get_variable(label, line)

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        raise "Abstract class"

    def translate(self) -> list[str]:
        arguments_string = ",".join(self.arguments)
        
        spacing_length = self.program.config.tabspaces - len(self.label) if self.labeled else self.program.config.tabspaces
        if spacing_length <= 0:
            raise TranslationError(f"Label too long. {self}")
        
        spacing = " " * spacing_length
        return [f"{self.label if self.label else ''}{spacing}{self.command} {arguments_string} {self.map_comment if self.synthetic else ''}"]


class VariableLexer(Lexer):

    @classmethod
    def create(cls, line: Line, parent: Lexer, program: Lexer, label: str, init_value: str) -> "VariableLexer":
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