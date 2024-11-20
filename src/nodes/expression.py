from ..tree import Node
from ..tokenizer import Token
from .scope import Context, Symbol
from typing import Type
from .types import ValueType, TYPES, Int, Char, Bool, Void, Array, decide_literal_type
from .node import AbstractSyntaxTreeNode as ASTNode

class ExpressionNode(ASTNode):
    def __init__(self, token: Token, children: list[ASTNode], parser: "Parser"):
        super().__init__(token, children, parser)
        self.type: ValueType

class FunctionCallNode(ExpressionNode):
    def __init__(self, token: Token, arguments: list[ASTNode], parser: "Parser"):
        super().__init__(token, arguments, parser)

    def register(self) -> None:
        self.scope.resolve_symbol(self.token).reference(self)
        #TODO: check it is a function and not variable declaration

class BinaryOperationNode(ExpressionNode):
    def __init__(self, token: Token, left: ASTNode, right: ASTNode, parser: "Parser"):
        super().__init__(token, [left, right], parser)

class UnaryOperationNode(ExpressionNode):
    def __init__(self, token: Token, child: ASTNode, parser: "Parser"):
        super().__init__(token, [child], parser)
        self.child = child
        self.operation: str = token.string

class BinaryNode(BinaryOperationNode):
    pass

class AdditiveNode(BinaryOperationNode):
    pass

class MultiplicativeNode(BinaryOperationNode):
    pass

class ComparisonNode(BinaryOperationNode):
    pass

class LogicalNode(BinaryOperationNode):
    pass

class VariableReferenceNode(ExpressionNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

    def register(self) -> None:
        symbol = self.scope.resolve_symbol(self.token)
        symbol.reference(self)
        #TODO: check it is a variable and not function declaration

class LiteralNode(ExpressionNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)
        self.val_type: ValueType = decide_literal_type(self.token)

class ArrayLiteralNode(ExpressionNode):
    def __init__(self, token: Token, elements: list[ExpressionNode], parser: "Parser"):
        super().__init__(token, elements, parser)
        self.elements = elements
        self.val_type = Array(self.elements[0].val_type, size=len(elements))

class IndexRetrievalNode(UnaryOperationNode):
    def __init__(self, token: Token, child: ASTNode, parser: "Parser"):
        super().__init__(token, child, parser)