from ..tree import Node
from ..tokenizer import Token, StringLiteralToken, AdditiveToken, MultiplicativeToken, MinusToken, StarToken, BinaryNotToken, LogicalNotToken, NameToken
from .scope import Context, Symbol
from typing import Type
from .types import ExpressionType, FunctionType, VariableType, ValueType, Comparator, VALUE_TYPES, Array, Int, Pointer, Char
from .node import AbstractSyntaxTreeNode as ASTNode
from ..errors import TypeError

class ExpressionNode(ASTNode):
    def __init__(self, token: Token, children: list[ASTNode], parser: "Parser"):
        super().__init__(token, children, parser)
        self.node_type: ExpressionType

class FunctionCallNode(ExpressionNode):
    def __init__(self, name_token: Token, arguments: list[ASTNode], parser: "Parser"):
        super().__init__(name_token, arguments, parser)
        self.arguments = arguments
        self.simulated: bool = False

    def register(self) -> None:

        self.symbol = self.scope.resolve_symbol(self.token)
        self.symbol.reference(self)

        definition = self.symbol.node
        if not FunctionType.match(definition.node_type):
            raise TypeError(f"Cannot call \"{self.token.string}\" of type {definition.node_type} as a function", self.token.line, defined_at=definition.token.line)
        
        self.node_type: ValueType = Comparator.function_call_value(definition.node_type, [arg.node_type for arg in self.arguments], node=self)


class CastNode(ExpressionNode):

    def __init__(self, token: Token, result_type: ValueType, operand: ExpressionNode, signed: bool, parser: "Parser"):
        super().__init__(token, [operand], parser)
        self.operand = operand
        self.result_type: ValueType = result_type
        self.signed: bool = signed

    def register(self) -> None:
        self.node_type: ValueType = Comparator.cast(self.operand.node_type, self.result_type, node=self)


class BinaryOperationNode(ExpressionNode):
    # boilerplate!
    def __init__(self, operation_token: Token, left: ExpressionNode, right: ExpressionNode, parser: "Parser"):
        super().__init__(operation_token, [left, right], parser)
        self.left = left
        self.right = right

class UnaryOperationNode(ExpressionNode):
    # not boilerplate!
    def __init__(self, token: Token, child: ASTNode, parser: "Parser"):
        super().__init__(token, [child], parser)
        self.operand = child
        self.operation: str = token.string
    
    def register(self) -> None:

        if MinusToken.match(self.token):
            self.node_type: ValueType = Comparator.unary_arithmetic(self.operand.node_type, node=self)

        elif LogicalNotToken.match(self.token):
            self.node_type: ValueType = Comparator.unary_logic(self.operand.node_type, node=self)

        elif BinaryNotToken.match(self.token):
            self.node_type: ValueType = Comparator.unary_arithmetic(self.operand.node_type, node=self)
        
        else:
            raise TypeError(f"Unknown unary operation \"{self.token.string}\"", self.token.line)


class BinaryNode(BinaryOperationNode):
    def register(self):
        self.node_type: ValueType = Comparator.arithmetic(self.left.node_type, self.right.node_type, node=self)

class AdditiveNode(BinaryOperationNode):
    def register(self):
        self.node_type: ValueType = Comparator.arithmetic(self.left.node_type, self.right.node_type, node=self)

class MultiplicativeNode(BinaryOperationNode):
    def register(self):
        self.node_type: ValueType = Comparator.arithmetic(self.left.node_type, self.right.node_type, node=self)

class ComparisonNode(BinaryOperationNode):
    def register(self):
        self.node_type: ValueType = Comparator.comparison(self.left.node_type, self.right.node_type, node=self)

class LogicalNode(BinaryOperationNode):
    def register(self):
        self.node_type: ValueType = Comparator.logic(self.left.node_type, self.right.node_type, node=self)


class VariableReferenceNode(ExpressionNode):
    def __init__(self, token: Token, pointer: bool, dereference: bool, index: ExpressionNode | None, parser: "Parser"):
        super().__init__(token, [index] if index is not None else [], parser)
        self.pointer: bool = pointer
        self.dereference: bool = dereference
        self.index: ExpressionNode | None = index

    def register(self) -> None:
        symbol = self.scope.resolve_symbol(self.token)
        self.symbol = symbol
        symbol.reference(self)
        var_type: VariableType = symbol.node.node_type
        self.node_type = Comparator.variable_reference(
            var_type,
            self.pointer,
            self.dereference,
            index=(self.index.node_type if self.index is not None else None),
            node=self
        )

class LiteralNode(ExpressionNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)
        self.node_type: ExpressionType = ExpressionType.decide(token)

class StringReferenceNode(ExpressionNode):
    def __init__(self, token: Token, str_token: StringLiteralToken, parser: "Parser"):
        super().__init__(token, [], parser)
        self.string_literal: StringLiteralToken = str_token
        self.node_type = Pointer(Array(Char, None))

class ArrayLiteralNode(ExpressionNode):
    def __init__(self, token: Token, elements: list[ExpressionNode], parser: "Parser"):
        super().__init__(token, elements, parser)
        self.elements = elements

    def register(self) -> None:
        self.node_type = Array(self.elements[0].node_type if self.elements else None, size=len(self.elements))

    def verify(self) -> None:
        for element in self.elements:
            if not Comparator.match(element.node_type, self.node_type.element_type):
                raise TypeError(f"Mixed types in array literal, adding type {element.node_type} to array of type {self.node_type}", self.token.line)


class AssemblyExpressionNode(ExpressionNode):
    
    def __init__(self, token: Token, assembly_expression: str, parser: "Parser"):
        super().__init__(token, [], parser)
        self.assembly_expression: str = assembly_expression
        self.node_type = Int