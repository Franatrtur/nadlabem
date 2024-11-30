from ..tree import Node
from ..tokenizer import Token, Line, NameToken
from ..errors import NameError
from typing import Union

class Context(Node):

    def __init__(self, node: "Parser", parent: Union["Context", None] = None):
        super().__init__(parent)
        self.parent: Context
        self.node = node
        self.symbols: dict[str, Symbol] = {}
        self.ids: set[str] = set()

    def register_symbol(self, symbol: "Symbol", local: bool = True):
        #TODO: set bubble up to false when not strict config
        #this would allow local variables to override globals when not in strict mode
        found = self.has_name(symbol.name, bubble_up= not local)
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

    def generate_id(self, name_suggestion: str) -> str:
        symbol_id = name_suggestion
        num = 1
        while symbol_id in self.root.ids:
            symbol_id = name_suggestion + str(num)
            num += 1
        self.root.ids.add(symbol_id)
        return symbol_id

    def __str__(self):
        return f"Context({self.node.__class__.__name__}({self.node.token.line if self.node.token else 0}))"
    def __repr__(self):
        return str(self)


class Symbol:

    def __init__(self, name_token: NameToken, node: "StatementNode"):
        self.name: str = name_token.string
        self.node: "StatementNode" = node
        self.references: list["Node"] = [self.node]
        self.scope: Context = None
        self._id: str = None

    @property
    def is_global(self) -> bool:
        return self.scope.is_root
        
    @property
    def id(self) -> str:
        if self._id is None:
            self._id = self.generate_id()
        return self._id

    def generate_id(self) -> str:
        symbol_id = self.name
        num = 1
        while symbol_id in self.scope.root.ids:
            symbol_id = self.name + str(num)
            num += 1
        self.scope.root.ids.add(symbol_id)
        return symbol_id

    def reference(self, node: "Node"):
        self.references.append(node)

    def __str__(self):
        return f"Symbol({self.name})"


