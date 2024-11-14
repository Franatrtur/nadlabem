from ..tree import Node
from ..tokenizer import Token, Line, NameToken
from ..errors import NameError
from typing import Union

class Context(Node):

    def __init__(self, block: "Parser", parent: Union["Context", None] = None):
        super().__init__(parent)
        self.block = block
        self.symbols: dict[str, "Symbol"] = {}

    def register_symbol(self, symbol: "Symbol"):
        if symbol.name in self.symbols:
            raise NameError(f"Symbol '{symbol.name}' is already defined", symbol.declaration.token.line)
        symbol.scope = self
        self.symbols[symbol.name] = symbol

    def resolve_symbol(self, name_token: NameToken) -> "Symbol":
        name = name_token.string
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent is not None and not self.is_root:
            return self.parent.resolve_symbol(name)
        else:
            raise NameError(f"Undefined name '{name}'", name_token.line)

    def __str__(self):
        return f"Context({self.block.name})"


class Symbol:

    def __init__(self, name_token: NameToken, node: "StatementNode"):
        self.name = name_token.string
        self.declaration = node
        self.references: list["Node"] = [self.declaration]
        self.scope: Context = None

    def reference(self, node: "Node"):
        self.references.append(node)

    def __str__(self):
        return f"Symbol({self.name})"


