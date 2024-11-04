from .tokenizer import Line
from .config import TranslationConfig
from .ui import progress_bar
from .lexer import Lexer
from .errors import NameError, ParsingError


class DirectiveLexer(Lexer):

    def __init__(self, line: Line, parent: Lexer):
        super().__init__(line, parent)
        self.registered = False

    def register(self) -> None:
        """Attaches self to program. Signifies that the instruction is saturated completely.
        it is finished and no more changes will be made before translation"""
        if self.label and not self.registered:
            self.program.register(self)
            self.registered = True

    @classmethod
    def create(cls, parent: Lexer, command: str, arguments: list[str] = [], label: str | None = None, done: bool = True) -> "DirectiveLexer":
        instruction = cls(parent.start_line, parent)

        instruction.command = command
        instruction.arguments = arguments if arguments else []
        instruction.synthetic = True

        #attach to program
        instruction.label = label
        if done:
            instruction.register()

        return instruction

    @classmethod
    def create_if_doesnt_exist(cls, parent: Lexer, command: str, arguments: list[str] = [], label: str | None = None) -> "DirectiveLexer":
        if label and label in parent.program.labeled:
            return parent.program.labeled[label]
        else:
            return cls.create(parent, command, arguments, label)

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        raise "Abstract class"

    def translate(self, mapping: bool = False) -> list[str]:
        arguments_string = ",".join(str(arg) for arg in self.arguments)
        
        spacing_length = self.program.config.tabspaces - len(self.label) if self.label else self.program.config.tabspaces
        if spacing_length <= 0:
            raise NameError(f"Label \"{self.label}\" is too long > {self.program.config.tabspaces} characters. {self}", self.start_line)
        
        spacing = " " * spacing_length
        comment = self.map_comment if mapping and self.synthetic else self.comment
        translated = f"{self.label if self.label else ''}{spacing}{self.command.upper()} {arguments_string}"
        comment_spacing = max(24 - len(translated), 1)
        return [translated + " " * comment_spacing + comment]




class VariableLexer(DirectiveLexer):

    def register(self) -> None:
        super().register()
        self.parent = self.program

    @classmethod
    def create(cls, parent: Lexer, label: str, init_value: str | int = 0, done: bool = True) -> "VariableLexer":
        var = super().create(parent, command=None, label=label, done=False)
        var.init_value = init_value
        if done:
            var.register()
        return var

    @classmethod
    def create_if_doesnt_exist(cls, parent: Lexer, label: str, init_value: str | int = 0) -> "VariableLexer":
        if label in parent.program.variables:
            return parent.program.get_variable(label, parent.start_line)
        else:
            return cls.create(parent, label, init_value)