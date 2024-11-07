from .tokenizer import Line
from .tree import Node
from .config import TranslationConfig

class Lexer(Node):

    def __init__(self, line: Line, parent: "Lexer"):
        super().__init__(parent, root=parent.root if parent else None)
        self.program: "Program" = self.root
        self.start_line = line
        self.comment = line.comment

    @staticmethod
    def detect(self, line: Line) -> bool:
        pass

    def process(self, line: Line, stack: list["Lexer"]) -> bool: #vrátí, jestli to spapal
        pass

    # returns a list of string lines
    def translate(self) -> list[str]:
        pass

    # returns a mapping from the parsed lexer to the original program
    @property
    def mapping(self) -> str:
        return f"{self.start_line.string} (line {self.start_line.number})"

    @property
    def map_comment(self):
        return f";{self.mapping}" if self.root.config.generate_mapping else self.comment

    def __str__(self) -> str:
        if self.children:
            string_children = ', '.join([str(child) for child in self.children])
            return f"{self.__class__.__name__}({self.mapping}, [{string_children}])"
        return f"{self.__class__.__name__}({self.mapping})"

    def __repr__(self) -> str:
        return str(self)