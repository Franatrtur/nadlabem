from ..tree import Node
from ..tokenizer import Token, AdditiveToken, MultiplicativeToken, MinusToken, StarToken, BinaryNotToken, NegationToken
from .scope import Context, Symbol
from typing import Type
from .types import Int, Char, Bool, Void, Array, ExpressionType, FunctionType, VariableType, ValueType, VALUE_TYPES
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
        if self.token.string == "len":
            if len(self.arguments) != 1:
                raise TypeError(f"Expected 1 argument for array len, got {len(self.arguments)} arguments", self.token.line)
            if not isinstance(self.arguments[0].node_type, Array):
                raise TypeError(f"Cannot call array len on type {self.arguments[0].node_type}", self.token.line)
            self.node_type = Int
            self.simulated = True
            return

        symbol = self.scope.resolve_symbol(self.token)
        symbol.reference(self)
        definition = symbol.node
        if not FunctionType.match(definition.node_type):
            raise TypeError(f"Cannot call \"{self.token.string}\" of type {definition.node_type} as a function", self.token.line, defined_at=definition.token.line)
        
        function_type: FunctionType = definition.node_type
        if not FunctionType.match(function_type):
            raise TypeError(f"Expected function type, got type {function_type}", self.token.line)
        if not function_type.match_params([arg.node_type for arg in self.arguments]):
            expected = ", ".join(map(str, function_type.parameters))
            got = ", ".join([str(arg.node_type) for arg in self.arguments])
            raise TypeError(f"Expected arguments ({expected}), got ({got})", self.token.line)
        if Void == function_type.return_type:
            raise TypeError(f"Cannot call \"{self.token.string}\" of return type {function_type.node_type} in an expression, as it returns void", self.token.line, defined_at=definition.token.line)
        self.node_type: ExpressionType = function_type.return_type

class BinaryOperationNode(ExpressionNode):
    # boilerplate!
    def __init__(self, operation_token: Token, left: ExpressionNode, right: ExpressionNode, parser: "Parser"):
        super().__init__(operation_token, [left, right], parser)
        self.left = left
        self.right = right
    
    def _register_type(self, default_type: ExpressionType, allowed_types: list[ExpressionType], allow_mixed: bool = True) -> None:
        assert_value_type(self.left, self)
        assert_value_type(self.right, self)
        
        if self.left.node_type not in allowed_types or self.right.node_type not in allowed_types:
            allowed = ", ".join(map(str, allowed_types))
            raise TypeError(f"Cannot apply operation {self.token.string} on types {self.left.node_type} and {self.right.node_type}", self.token.line, expected_types=allowed)
        
        if not allow_mixed and self.left.node_type != self.right.node_type:
            self.config.warn(TypeError(f"Mixed operands in operation {self.token.string} on types {self.left.node_type} and {self.right.node_type}", self.token.line))
        
        self.node_type: ExpressionType = self.left.node_type if self.right.node_type == default_type else default_type

def assert_value_type(child: ExpressionNode, parent: ExpressionNode) -> None:
    if not ValueType.match(child.node_type):
        allowed = ", ".join(t.__name__ for t in VALUE_TYPES.keys())
        raise TypeError(f"Cannot apply operation {parent.token.string} on type {child.node_type}", parent.token.line, expected_types=allowed)

class UnaryOperationNode(ExpressionNode):
    # not boilerplate!
    def __init__(self, token: Token, child: ASTNode, parser: "Parser"):
        super().__init__(token, [child], parser)
        self.child = child
        self.operation: str = token.string
    
    def register(self) -> None:

        if MinusToken.match(self.token):
            assert_value_type(self.child, self)
            self.node_type = Int
            if Int != self.child.node_type:
                self.config.warn(TypeError(f"Expected minus ({self.token.string}) application on ints, but applied on type {self.child.node_type}", self.token.line))

        elif NegationToken.match(self.token):
            assert_value_type(self.child, self)
            self.node_type = Bool
            if Bool != self.child.node_type:
                self.config.warn(TypeError(f"Expected logical not ({self.token.string}) application on bools, but applied on type {self.child.node_type}", self.token.line))
        
        elif BinaryNotToken.match(self.token):
            assert_value_type(self.child, self)
            self.node_type = Int
            if Int != self.child.node_type:
                self.config.warn(TypeError(f"Expected binary not ({self.token.string}) application on ints, but applied on type {self.child.node_type}", self.token.line))

        elif StarToken.match(self.token):
            self.node_type = Int
            if not isinstance(self.child, VariableReferenceNode):
                raise TypeError(f"Can only de-reference variables, cannot de-reference expression", self.token.line)
        
        else:
            raise TypeError(f"Unknown unary operation \"{self.token.string}\"", self.token.line)


class BinaryNode(BinaryOperationNode):
    def register(self):
        self._register_type(default_type=Int, allowed_types=[Int, Char], allow_mixed=True)

class AdditiveNode(BinaryOperationNode):
    def register(self):
        self._register_type(default_type=Int, allowed_types=[Int, Char, Bool], allow_mixed=True)

class MultiplicativeNode(BinaryOperationNode):
    def register(self):
        self._register_type(default_type=Int, allowed_types=[Int, Char, Bool], allow_mixed=True)

class ComparisonNode(BinaryOperationNode):
    def register(self):
        self._register_type(default_type=Bool, allowed_types=[Int, Char, Bool], allow_mixed=False)
        self.node_type = Bool
        if Bool == self.left.node_type or Bool == self.right.node_type:
            self.config.warn(TypeError(f"Comparison {self.token.string} of types {self.left.node_type} and {self.right.node_type}", self.token.line))

class LogicalNode(BinaryOperationNode):
    def register(self):
        self._register_type(default_type=Bool, allowed_types=[Bool], allow_mixed=False)
        self.node_type = Bool
        if Bool != self.left.node_type or Bool != self.right.node_type:
            self.config.warn(TypeError(f"Logical operation {self.token.string} of types {self.left.node_type} and {self.right.node_type}", self.token.line))

class VariableReferenceNode(ExpressionNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

    def register(self) -> None:
        symbol = self.scope.resolve_symbol(self.token)
        self.symbol = symbol
        symbol.reference(self)
        var_type: VariableType = symbol.node.node_type
        if not VariableType.match(var_type):
            raise TypeError(f"Cannot reference \"{self.token.string}\" of type {var_type} as a variable", self.token.line, defined_at=symbol.node.token.line)
        self.node_type: ExpressionType = var_type.expression_type

class LiteralNode(ExpressionNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)
        self.node_type: ExpressionType = ExpressionType.decide(token)

class ArrayLiteralNode(ExpressionNode):
    def __init__(self, token: Token, elements: list[ExpressionNode], parser: "Parser"):
        super().__init__(token, elements, parser)
        self.elements = elements

    def register(self) -> None:
        self.node_type = Array(self.elements[0].node_type, size=len(self.elements))

    def verify(self) -> None:
        for element in self.elements:
            if not element.node_type.match(self.node_type.element_type):
                raise TypeError(f"Cannot add element of type {element.node_type} to array of type {self.node_type}", self.token.line)
            elif not element.node_type.matches(self.node_type.element_type, strict=False):
                self.config.warn(TypeError(f"Mixed types in array literal, adding element of type {element.node_type} to array of type {self.node_type}", self.token.line))

class IndexRetrievalNode(ExpressionNode):
    def __init__(self, token: Token, array_node: ExpressionNode, index: ExpressionNode, parser: "Parser"):
        super().__init__(token, [array_node, index], parser)
        self.array_node = array_node
        self.index = index

    def verify(self) -> None:
        if not isinstance(self.array_node.node_type, Array):
            raise TypeError(f"Cannot index \"{self.token.string}\" of type {self.array_node.node_type} as an array", self.token.line, defined_at=self.array_node.token.line)
        self.node_type: ExpressionType = self.array_node.node_type.element_type