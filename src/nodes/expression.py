from ..tree import Node
from ..tokenizer import Token, AdditiveToken, MultiplicativeToken
from .scope import Context, Symbol
from typing import Type
from .types import VALUE_TYPES, Int, Char, Bool, Void, Array, ExpressionType, FunctionType
from .node import AbstractSyntaxTreeNode as ASTNode
from ..errors import TypeError

class ExpressionNode(ASTNode):
    def __init__(self, token: Token, children: list[ASTNode], parser: "Parser"):
        super().__init__(token, children, parser)
        self.node_type: ExpressionType

class FunctionCallNode(ExpressionNode):
    def __init__(self, name_token: Token, arguments: list[ASTNode], parser: "Parser"):
        super().__init__(name_token, arguments, parser)

    def register(self) -> None:
        symbol = self.scope.resolve_symbol(self.token)
        symbol.reference(self)
        defintion = symbol.node
        if not FunctionType.match(defintion.node_type):
            raise TypeError(f"Cannot call \"{self.token.string}\" of type {defintion.node_type} as a function", self.token.line, defined_at=defintion.token.line)
        if Void == defintion.return_type:
            raise TypeError(f"Cannot call \"{self.token.string}\" of type {defintion.node_type} in an expression, as it returns void", self.token.line, defined_at=defintion.token.line)
        self.node_type: ExpressionType = defintion.return_type

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
        self.node_type: ExpressionType = ExpressionType.decide(token)

class ArrayLiteralNode(ExpressionNode):
    def __init__(self, token: Token, elements: list[ExpressionNode], parser: "Parser"):
        super().__init__(token, elements, parser)
        self.elements = elements
        self.node_type = Array(self.elements[0].node_type, size=len(elements))

    def verify(self) -> None:
        for element in self.elements:
            if not element.node_type == self.node_type.element_type:
                raise 

class IndexRetrievalNode(UnaryOperationNode):
    def __init__(self, token: Token, array: ExpressionNode, index: ExpressionNode, parser: "Parser"):
        super().__init__(token, [array, index], parser)
        self.array = array
        self.index = index
        #TODO: check array is an array
        self.node_type = self.array.node_type.base_type