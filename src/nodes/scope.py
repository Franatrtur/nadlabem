from ..tree import Node
from ..tokenizer import Token, Line, NameToken
from ..errors import NameError
from typing import Union

class Context(Node):

    def __init__(self, node: "ASTNode", parent: Union["Context", None] = None):
        super().__init__(parent)
        self.parent: Context
        self.node = node
        self.symbols: dict[str, Symbol] = {}
        self.ids: set[str] = set()

    def register_symbol(self, symbol: "Symbol", local: bool = True):
        found = self.find_name(symbol.name)
        if found is not None:
            raise NameError(f"Cannot redefine name {repr(symbol.name)}", symbol.node.token.line, defined_at=found.node.token.line)
        symbol.scope = self
        self.symbols[symbol.name] = symbol

    def find_name(self, name: str) -> "Symbol | None":
        return self.symbols.get(name, None)

    def get_symbol(self, name_token: NameToken) -> "Symbol":
        return self.resolve_names(name_token, name_token.components)

    def resolve_names(self, name_token: NameToken, components: list[str]) -> "Symbol":
        name = components[0]

        if len(components) == 1:
            found = self.find_name(name)
            if found is not None:
                return found

        return self.parent.resolve_names(name_token, components)

    def generate_id(self, name_suggestion: str) -> str:
        name_suggestion = "_" if self.config.obfuscate else name_suggestion  # forget label on obfuscation
        symbol_id = name_suggestion
        num = 1
        while symbol_id in self.root.ids or symbol_id in RESERVED_NAMES:
            symbol_id = name_suggestion + str(num)
            num += 1
        self.root.ids.add(symbol_id)
        return symbol_id

    def __str__(self):
        return f"{self.__class__.__name__}({repr(self.node)})"
    def __repr__(self):
        return str(self)


class Namespace(Context):

    def __init__(self, node: "ASTNode", parent: Union["Context", None] = None):
        super().__init__(node, parent)
        self.config = node.config
        self.modules: dict[str, Namespace] = {}
        self.direct: list[Namespace] = []   # ordered so later defined namespaces override earlier ones

        if parent and not isinstance(parent, Namespace):
            raise NameError("Cannot define namespace in functions local context", node.token.line, parent=parent)

    def named_space(self, name: str) -> "None | Namespace":
        if name in self.modules:
            return self.modules[name]

        for module in self.direct:
            found = module.named_space(name)
            if found is not None:
                return found
    
        return None

    def relate(self, name_token: NameToken | None, namespace: "Namespace"):
        if name_token is None:
            self.direct.append(namespace)
        else:
            taken = self.named_space(name_token.string)
            if taken:
                raise NameError(f"Duplicate namespace name {repr(name_token.string)}", line=name_token.line, defined_at=taken.node.token.line)
            self.modules[name_token.string] = namespace

    def resolve_names(self, name_token: NameToken, components: list[str], forward: bool = False) -> "Symbol":
        name = components[0]

        if len(components) == 1:
            if name in self.symbols:
                return self.symbols[name]

        elif name in self.modules:
            return self.modules[name].resolve_names(name_token, components[1:], forward=False)

        for module in self.direct:
            attempt: Symbol | None = module.resolve_names(name_token, components, forward=True)
            if attempt is not None:
                return attempt

        if forward:
            return None

        nametype: str = f"namespace {repr(name)} in compound name {repr(name_token.string)}" if len(components) > 1 else f"name {repr(name)}"
        raise NameError(f"Undefined {nametype}", name_token.line, context=self)


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
            self._id = self.scope.generate_id(self.name)
        return self._id

    def reference(self, node: "Node"):
        self.references.append(node)

    @property
    def is_relevant(self):
        for node in self.references:
            if node.is_connected and node is not self.node:
                # print(self, "is relevant, referenced by", repr(node))
                return True
        # print(self, "is not relevant")
        return False

    def __str__(self):
        return f"Symbol({repr(self.name)})"
    def __repr__(self):
        return str(self)


RESERVED_NAMES: set[str] = {
    "dno", "code", "start", "stack", "data", "sp", "bp",
    "di", "ax", "bx", "cx", "dx", "cs", "ss", "ds", "cpu",
    "segment", "exit", "heap", "ok", "error", "true", "false"
}