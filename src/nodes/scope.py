from ..tree import Node
from ..tokenizer import Token, Line, NameToken
from ..errors import NameError
from typing import Union

class Context(Node):

    def __init__(self, block: "Parser", parent: Union["Context", None] = None):
        super().__init__(parent)
        self.parent: Context
        self.block = block
        self.symbols: dict[str, "Symbol"] = {}

    def register_symbol(self, symbol: "Symbol"):
        #TODO: set bubble up to false when not strict config
        #this would allow local variables to override globals when not in strict mode
        found = self.has_name(symbol.name, bubble_up=True)
        if found is not None:
            raise NameError(f"Cannot redefine name '{symbol.name}'", symbol.node.token.line, defined_at=found.node.token.line)
        symbol.scope = self
        self.symbols[symbol.name] = symbol

    def has_name(self, name: str, bubble_up: bool) -> Union["Symbol", None]:
        if name in self.symbols:
            return self.symbols[name]
        if bubble_up and self.parent is not None and not self.is_root:
            return self.parent.has_name(name, bubble_up)
        return None

    def resolve_symbol(self, name_token: NameToken, bubble_up: bool = True) -> "Symbol":
        name = name_token.string
        if name in self.symbols:
            return self.symbols[name]
        elif bubble_up and self.parent is not None and not self.is_root:
            return self.parent.resolve_symbol(name_token, bubble_up)
        else:
            raise NameError(f"Undefined name '{name}'", name_token.line, context=self, tried_bubble_up=bubble_up)

    def __str__(self):
        return f"Context({self.block.__class__.__name__}({self.block.token.line if self.block.token else 0}))"
    def __repr__(self):
        return str(self)


class Symbol:

    def __init__(self, name_token: NameToken, node: "StatementNode"):
        self.name = name_token.string
        self.node = node
        self.references: list["Node"] = [self.node]
        self.scope: Context = None

    def reference(self, node: "Node"):
        self.references.append(node)

    def __str__(self):
        return f"Symbol({self.name})"


