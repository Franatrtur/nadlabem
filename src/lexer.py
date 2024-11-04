from .tokenizer import Line
from .tree import Tree
from .config import TranslationConfig

class Lexer(Tree):

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


class SyntheticLexer(Lexer):

    synthetic = True

    @classmethod
    def create(cls, parent: Lexer) -> Lexer:
        return cls(parent.start_line, parent)

    def translate(self, mapping: bool = False) -> list[str]:
        translated = []
        for child in self.children:
            translated.extend(child.translate(
                mapping = mapping and (
                    child is self.children[0] #or isinstance(child, SyntheticLexer)
                )
            ))
        return translated