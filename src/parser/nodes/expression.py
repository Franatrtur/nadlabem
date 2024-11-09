from ...tree import Node
from ...tokenizer import Token

class AbstractSyntaxTreeNode(Node):
    def __init__(self, token: Token, parent: AbstractSyntaxTreeNode, children: list[Node]):
        super().__init__(parent)
        self.children = children
        self.token = token
        self.context = parent.context

class BinaryNode(AbstractSyntaxTreeNode):
    def __init__(self, token: Token, parent: Node, left: Node, right: Node):
        super().__init__(parent, token)
        self.left = left
        self.right = right

class UnaryNode(AbstractSyntaxTreeNode):
    def __init__(self, token: Token, parent: Node, child: Node):
        super().__init__(parent, token)
        self.child = child

class ValueNode(AbstractSyntaxTreeNode):
    def __init__(self, token: Token, parent: Node):
        super().__init__(parent, token)
        self.value = token.string

class VariableReferenceNode(ValueNode):
    pass

class FunctionCallValueNode(ValueNode):
    def __init__(self, token: Token, parent: Node, arguments: list[Node]):
        super().__init__(parent, token)
        self.arguments = arguments