from ..tree import Node
from ..tokenizer import Token
from .scope import Context
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
        # (nodes with their own context) have been registered first
        for child in self.children:
            if child.scope != child.context:
                child.register()
        for child in self.children:
            if child.scope == child.context:
                child.register_children()
                child.register()
        for child in self.children:
            if child.scope != child.context:
                child.register_children()

        for child in self.children:
            child.verify()

    def prune(self) -> bool:
        return False

    def prune_children(self) -> None:
        for child in self.children:
            child.prune_children()
            if child.prune():
                self.children.remove(child)

    def verify(self) -> None:
        pass

    def __str__(self):
        self_str = f"{self.__class__.__name__}({self.token})" + (" - "+ str(self.node_type) if self.node_type is not None else "")
        
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


class ProgramNode(AbstractSyntaxTreeNode):

    def __init__(self, statements: list[AbstractSyntaxTreeNode], parser: "ProgramParser"):
        super().__init__(None, statements, parser)
        self.parent = None
        self.root = self  # top level node
        self.statements = statements
        self.context = Context(self, None)
        self.context.root = self.context.root = self.context  #top level context
    
    def validate(self):
        self.link(parent=None)
        self.register_children()  # registers and validates tree
        self.prune_children()
        print(self)
