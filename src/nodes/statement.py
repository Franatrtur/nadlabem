from ..tree import Node
from ..tokenizer import Token, TypeToken
from .scope import Context, Symbol
from typing import Type
from .types import VariableType, FunctionType, Void, Int, Char, Bool, Array, DeclarationType, ExpressionType, ValueType
from .node import AbstractSyntaxTreeNode as ASTNode
from .expression import ExpressionNode
from ..errors import TypeError


#TODO: implement closest_parent( of type) IN NODE.PY  for break and continuenodes to find their relevant parents

class StatementNode(ASTNode):
    pass

class CodeBlockNode(StatementNode):
    def __init__(self, token: Token, children: list[StatementNode], parser: "Parser"):
        super().__init__(token, children, parser)
        self.statements = children
        self.context = Context(block=self, parent=self.scope)

    def register_children(self):
        # do the whole layer before nested layers, except blocks in blocks
        for child in self.children:
            child.register()
            if isinstance(child, CodeBlockNode):
                child.register_children()

        for child in self.children:
            if not isinstance(child, CodeBlockNode):
                child.register_children()

class VariableDeclarationNode(StatementNode):
    def __init__(self, name: Token, value: ExpressionNode, var_type: VariableType, parser: "Parser"):
        super().__init__(name, [value], parser)
        self.value = value
        self.name_token = name
        self.node_type: VariableType = var_type

    def register(self) -> None:
        symbol = Symbol(self.name_token, node=self)
        self.context.register_symbol(symbol)

class AssignmentNode(StatementNode):
    def __init__(self, name_token: Token, value: ExpressionNode, parser: "Parser"):
        super().__init__(name_token, [value], parser)
        self.value = value

    def register(self) -> None:
        self.scope.resolve_symbol(self.token).reference(self)

class ArgumentDeclarationNode(StatementNode):
    def __init__(self, name_token: Token, var_type: VariableType, parser: "Parser"):
        super().__init__(name_token, [], parser)
        self.name_token = name_token
        self.node_type: VariableType = var_type

    def register(self) -> None:
        symbol = Symbol(self.name_token, node=self)
        self.context.register_symbol(symbol)

class FunctionDefinitonNode(StatementNode):
    def __init__(self, token: Token, arguments: list[ArgumentDeclarationNode], body: CodeBlockNode, node_type: FunctionType, parser: "Parser"):
        super().__init__(token, [*arguments, body], parser)
        self.arguments = arguments
        self.body = body
        self.name_token = token
        self.node_type: FunctionType = node_type
        self.context = Context(self, parent=self.scope)

    def register(self) -> None:
        symbol = Symbol(self.name_token, node=self)
        self.scope.register_symbol(symbol)

class ReturnNode(StatementNode):
    def __init__(self, token: Token, value: ExpressionNode | None, parser: "Parser"):
        super().__init__(token, [value], parser)
        self.value = value

def verify_condition(condition: ExpressionNode) -> None:
    condition_type = condition.node_type
    if not ValueType.match(condition_type):
        raise TypeError(f"Expected value type in condition, got {condition_type}", condition.token.line)
    if condition_type != Bool:
        condition.config.warn(TypeError(f"Expected bool type in condition, got {condition_type}", condition.token.line))


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
        super().__init__(token, [initialization, condition, increment, body], parser)
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

class BreakNode(StatementNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

class ContinueNode(StatementNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

class PassNode(StatementNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

class AssemblyNode(StatementNode):
    
    def __init__(self, token: Token, code: list[Token], parser: "Parser"):
        super().__init__(token, [], parser)
        self.code = code
        self.code_string = " ".join([token.string for token in code])