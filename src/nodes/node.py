from ..tree import Node
from ..tokenizer import Token
from .scope import Context, Namespace
from typing import Type
from ..config import CompilationConfig
from ..errors import NadLabemError

#TODO: implement closest_parent( of type) for break and continuenodes to find their relevant parents

class AbstractSyntaxTreeNode(Node):

    def __init__(self, token: Token, children: list[Node], parser: "Parser"):
        super().__init__(None)
        self.children = children
        self.token = token
        self.parser = parser
        self.context: Context = None
        self.scope: Context = None
        self.config: CompilationConfig = parser.config
        self.node_type = None
        
    def link(self, parent: "AbstractSyntaxTreeNode"):
        if parent is not None:
            self.set_parent(parent)
            self.scope: Context = parent.context
        else:
            self.scope = self.context

        if self.context is None:
            self.context = self.scope
        elif self.scope is not self.context:
            self.scope.add_child(self.context)

        for child in self.children:
            child.link(parent=self)

    def register(self) -> None:
        pass

    def register_children(self) -> None:
        # do nested layers before current layer
        # postorder traversal style
        # however, we have to make sure that functions
        # (nodes with their own non-namespace context) have been registered first
        for child in self.children:
            if child.has_closure:
                child.register()
        for child in self.children:
            if not child.has_closure:
                child.register_children()
                child.register()
        for child in self.children:
            if child.has_closure:
                child.register_children()

        for child in self.children:
            child.verify()

    @property       # returns whether a node is masked in first traversal (ie functions)
    def has_closure(self) -> bool:
        return self.scope != self.context and not isinstance(self.context, Namespace)

    def prune(self) -> bool:
        return False

    def prune_children(self) -> bool:
        removed: bool = False
        for child in self.children:
            removed = removed or child.prune_children()
            if child.prune():
                self.children.remove(child)
                child.parent = None
                removed = True
        return removed

    @property
    def is_connected(self) -> bool:
        return self.is_root or self.parent is not None and self.parent.is_connected

    def verify(self) -> None:
        pass

    def __str__(self):
        self_str = repr(self)
        
        for index, child in enumerate(self.children):
            is_last_child = (index == len(self.children) - 1)
            child_str = str(child)
            child_rows = child_str.split("\n")

            for row_index, row in enumerate(child_rows):
                bullet_point = "├─" if not is_last_child else "└─"
                connector = bullet_point if row_index == 0 else "│ "
                connector = connector if not (is_last_child and row_index > 0) else "  "
                self_str += f"\n  {connector}{row}"
                
        if len(self.children) > 2:
            self_str += "\n"
        return self_str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.token})" + (" - " + str(self.node_type) if self.node_type is not None else "")


class ProgramNode(AbstractSyntaxTreeNode):

    def __init__(self, statements: list[AbstractSyntaxTreeNode], parser: "ProgramParser"):
        super().__init__(None, statements, parser)
        self.parent = None
        self.root = self  # top level node
        self.context = Namespace(self, None)
        self.context.root = self.context  #top level context
        self.functions: list[AbstractSyntaxTreeNode] = []
    
    def validate(self):
        self.link(parent=None)
        self.register_children()  # registers and validates tree
        while self.prune_children():
            pass
        
