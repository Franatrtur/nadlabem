from ..tree import Node
from ..tokenizer import Token, TypeToken
from .scope import Context, Symbol
from typing import Type
from .types import VariableType, FunctionType, Void, Int, Char, Bool, Array, DeclarationType, ExpressionType, ValueType
from .node import AbstractSyntaxTreeNode as ASTNode
from .expression import ExpressionNode
from ..errors import TypeError

class StatementNode(ASTNode):
    pass

class CodeBlockNode(StatementNode):
    def __init__(self, token: Token, children: list[StatementNode], parser: "Parser"):
        super().__init__(token, children, parser)
        self.statements = children

    def register_children(self):
        
        # do the whole layer before nested layers, except blocks in blocks
        for child in self.children:
            child.register()
        for child in self.children:
            child.register_children()
        for child in self.children:
            child.verify()

class VariableDeclarationNode(StatementNode):
    def __init__(self, name: Token, value: ExpressionNode, var_type: VariableType, parser: "Parser"):
        super().__init__(name, [value], parser)
        self.value = value
        self.name_token = name
        self.node_type: VariableType = var_type

    def register(self) -> None:
        symbol = Symbol(self.name_token, node=self)
        self.context.register_symbol(symbol)

    def verify(self) -> None:
        value_type: ExpressionType = self.value.node_type
        if not self.node_type.matches(value_type, strict=isinstance(self.node_type.expression_type, Array)):
            pointed = "by pointer" if self.node_type.is_reference else "by value"
            raise TypeError(f"Cannot assign type {value_type} to type {self.node_type} {pointed}", self.token.line)

class AssignmentNode(StatementNode):
    def __init__(self, name_token: Token, value: ExpressionNode, parser: "Parser"):
        super().__init__(name_token, [value], parser)
        self.value = value

    def register(self) -> None:
        symbol = self.scope.resolve_symbol(self.token)
        self.variable: VariableDeclarationNode = symbol.node
        symbol.reference(self)

    def verify(self) -> None:
        variable_type: VariableType = self.variable.node_type
        value_type: ExpressionType = self.value.node_type
        if not variable_type.matches(value_type):
            raise TypeError(f"Cannot assign type {value_type} to type {variable_type}", self.token.line)

class ArgumentDeclarationNode(StatementNode):
    def __init__(self, name_token: Token, var_type: VariableType, parser: "Parser"):
        super().__init__(name_token, [], parser)
        self.name_token = name_token
        self.node_type: VariableType = var_type

    def register(self) -> None:
        symbol = Symbol(self.name_token, node=self)
        self.context.register_symbol(symbol)

class FunctionDefinitonNode(StatementNode):
    def __init__(self, token: Token, arguments: list[ArgumentDeclarationNode], body: CodeBlockNode, return_type: ExpressionType, parser: "Parser"):
        super().__init__(token, [*arguments, body], parser)
        self.arguments = arguments
        self.body = body
        self.name_token = token
        self.node_type = FunctionType(return_type, [arg.node_type for arg in arguments])
        self.context = Context(self, parent=self.scope)
        self.return_nodes: list[ReturnNode] = []

    def register(self) -> None:
        symbol = Symbol(self.name_token, node=self)
        self.scope.register_symbol(symbol)

    def verify(self) -> None:
        if not self.return_nodes and self.node_type.return_type != Void:
            self.config.warn(TypeError("Function has no return statement", self.token.line))

class ReturnNode(StatementNode):
    def __init__(self, token: Token, value: ExpressionNode | None, parser: "Parser"):
        super().__init__(token, [value] if value else [], parser)
        self.value: ExpressionNode | None = value

    # we cannot check it in register already and not in verify even though
    # function node types are assigned in __init__
    # because we have to wait for the expressions
    def verify(self) -> None:
        self.function: FunctionDefinitonNode = self.closest_parent(FunctionDefinitonNode)
        if self.function is None:
            raise TypeError("Return statement outside of function", self.token.line)
        function_type = self.function.node_type
        value_type = self.value.node_type if self.value is not None else Void
        if function_type.return_type != value_type:
             raise TypeError(f"Expected return type {function_type.return_type}, got type {value_type}", self.token.line)
        self.function.return_nodes.append(self)


def verify_condition(condition: ExpressionNode) -> None:
    condition_type = condition.node_type
    if not ValueType.match(condition_type):
        raise TypeError(f"Expected value type in condition, got type {condition_type}", condition.token.line)
    if condition_type != Bool:
        condition.config.warn(TypeError(f"Expected bool type in condition, got type {condition_type}", condition.token.line))


class IfNode(StatementNode):
    def __init__(self, token: Token, condition: ExpressionNode, body: CodeBlockNode, else_body: CodeBlockNode | None, parser: "Parser"):
        children = [condition, body] if else_body is None else [condition, body, else_body]
        super().__init__(token, children, parser)
        self.condition: ExpressionNode = condition
        self.body: StatementNode = body
        self.else_body: StatementNode | None = else_body

    def verify(self) -> None:
        verify_condition(self.condition)

class WhileNode(StatementNode):
    def __init__(self, token: Token, condition: ExpressionNode, body: CodeBlockNode, parser: "Parser"):
        super().__init__(token, [condition, body], parser)
        self.condition = condition
        self.body = body

    def verify(self) -> None:
        verify_condition(self.condition)

class ForNode(StatementNode):
    def __init__(self, token: Token, initialization: StatementNode, condition: ExpressionNode, increment: StatementNode, body: CodeBlockNode, parser: "Parser"):
        super().__init__(token, [initialization, condition, body, increment], parser)
        self.initialization = initialization
        self.condition = condition
        self.increment = increment
        self.body = body

    def verify(self) -> None:
        verify_condition(self.condition)

class FunctionCallStatementNode(StatementNode):
    #TODO: check return type is void if strict mode is on
    def __init__(self, token: Token, arguments: list[ExpressionNode], parser: "Parser"):
        super().__init__(token, arguments, parser)
        self.arguments = arguments

    def register(self) -> None:
        self.scope.resolve_symbol(self.token).reference(self)

    def verify(self) -> None:
        function_type: FunctionType = self.scope.resolve_symbol(self.token).node.node_type
        if not FunctionType.match(function_type):
            raise TypeError(f"Cannot call \"{self.token.string}\" of type {function_type} as a function", self.token.line)
        if not function_type.match_params([arg.node_type for arg in self.arguments]):
            expected = ", ".join(map(str, function_type.parameters))
            got = ", ".join([str(arg.node_type) for arg in self.arguments])
            raise TypeError(f"Expected argument types ({expected}), got ({got})", self.token.line)
        if Void != function_type.return_type:
            self.config.warn(TypeError(f"Non-void return type {function_type.return_type} in function call statement, assign the return value to a variable", self.token.line))

class BreakNode(StatementNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

    def register(self) -> None:
        self.loop: ForNode | WhileNode = self.closest_parent(WhileNode, ForNode)
        if self.loop is None:
            raise TypeError("Break statement outside of loop", self.token.line)

class ContinueNode(StatementNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

    def register(self) -> None:
        self.loop: ForNode | WhileNode = self.closest_parent(WhileNode, ForNode)
        if self.loop is None:
            raise TypeError("Break statement outside of loop", self.token.line)

class PassNode(StatementNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

class AssemblyNode(StatementNode):
    
    def __init__(self, token: Token, code: list[Token], parser: "Parser"):
        super().__init__(token, [], parser)
        self.code = code
        self.code_string = " ".join([token.string for token in code])