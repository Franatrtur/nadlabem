from ..tree import Node
from ..tokenizer import Token
from .scope import Context
from typing import Type
from .types import ValueType, TYPES

class AbstractSyntaxTreeNode(Node):

    def __init__(self, token: Token, children: list[Node], parser: "Parser"):
        super().__init__(None)
        self.children = children
        self.token = token
        self.parser = parser
        self.context: Context = None
        self.scope: Context = None
        
    def link(self, parent: "AbstractSyntaxTreeNode"):
        self.parent: AbstractSyntaxTreeNode = parent
        self.scope: Context = parent.context

        if self.context is None:
            self.context = self.scope
        else:
            self.context.set_parent(self.scope)

        for child in self.children:
            child.link(parent=self)

    def register(self):
        pass

    def register_children(self):
        # do the whole layer before nested layers
        for child in self.children:
            child.register()
        for child in self.children:
            child.register_children()

    def verify(self):
        for child in self.children:
            child.verify()

    #TODO: move this method to Node to be inherited by all node classes (src/tree.py/Node)
    def __str__(self):
        self_str = f"{self.__class__.__name__}(\"{self.token}\")"
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
        self.parent = self.root = self  # top level node
        self.statements = statements
        self.context = Context(self, None)
        self.context.root = self.context.parent = self.context  #top level context
    
    def validate(self):
        self.link(parent=self)
        self.register_children()
        self.verify()

    def register_children(self):
        # do the whole layer before nested layers, except blocks in blocks
        for child in self.children:
            child.register()
            if child.__class__.__name__ == "CodeBlockNode":
                child.register_children()

        for child in self.children:
            if child.__class__.__name__ != "CodeBlockNode":
                child.register_children()
