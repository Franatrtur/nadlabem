from .tokenizer import Line
from .tree import Tree
from .config import TranslationConfig

class Lexer(Tree):

    def __init__(self, line: Line, parent: "Lexer", root: "Lexer"):
        super().__init__(parent, root)
        self.start_line = line

    @staticmethod
    def detect(self, line: Line) -> bool:
        pass

    def process(self, line: Line, stack: list["Lexer"]) -> bool: #vrátí, jestli to spapal
        pass

    # returns a list of string lines
    def translate(self) -> list[str]:
        pass

    @property
    def map(self) -> str:
        return f"{self.start_line.string} (line {self.start_line.number})"

        
    @property
    def comment(self):
        return f";{self.map}" if self.root.config.generate_mapping else ""

    def __str__(self) -> str:
        if self.children:
            string_children = ', '.join([str(child) for child in self.children])
            return f"{self.__class__.__name__}({self.map}, [{string_children}])"
        return f"{self.__class__.__name__}({self.map})"



class VariableLexer(Lexer):

    @classmethod
    def create(cls, line: Line, parent: Lexer, root: Lexer, label: str, init_value: int) -> "VariableLexer":
        var = cls(line, parent, root)

        var.label = label
        var.init_value = value
        var.synthetic = True

        root.register_variable(var)

        return var

    def process(self, line: Line, stack: [Lexer]) -> bool: #vrátí, jestli to spapal
        raise "Abstract class"