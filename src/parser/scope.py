from ..tree import Tree
from ..tokenizer import Token, Line
from ..errors import NameError

class Context(Tree):

    def __init__(self, block: "Parser", parent: "Context" | None = None):
        super().__init__(parent)
        self.block = block
        self.names: dict[str, "Name"] = {}

    def register_name(self, name: "Name"):
        self.names[name.name] = name

    def resolve_name(self, name: str) -> "Name":
        if name in self.names:
            return self.names[name]
        elif self.parent is not None:
            return self.parent.resolve_name(name)
        else:
            raise NameError(f"Undefined name '{name}'")


class Name:

    def __init__(self, name: str, parser: "Parser", scope: Context):
        self.name = name
        self.name_type = name_type
        self.parser = parser
        self.declaration = self.parser.start_line
        self.references: list[Line] = [self.declaration]
        self.scope = scope

    def reference(self, line: Line):
        self.references.append(line)

    def __str__(self):
        return f"Name({self.name})"


