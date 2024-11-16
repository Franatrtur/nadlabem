from ..tree import Node
from ..tokenizer import Token, TypeToken
from .scope import Context, Symbol
from typing import Type
from .types import ValueType, TYPES
from .node import AbstractSyntaxTreeNode as ASTNode
from .expression import ExpressionNode


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
    def __init__(self, name: Token, value: ExpressionNode, type_token: TypeToken, parser: "Parser"):
        super().__init__(name, [value], parser)
        self.value = value
        self.name_token = name
        self.type_token = type_token

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
    def __init__(self, name_token: Token, type_token: TypeToken, parser: "Parser"):
        super().__init__(name_token, [], parser)
        self.name_token = name_token
        self.type_token = type_token

    def register(self) -> None:
        symbol = Symbol(self.name_token, node=self)
        self.context.register_symbol(symbol)

class FunctionDeclarationNode(StatementNode):
    def __init__(self, token: Token, arguments: list[ArgumentDeclarationNode], body: CodeBlockNode, type_token: TypeToken, parser: "Parser"):
        super().__init__(token, [*arguments, body], parser)
        self.arguments = arguments
        self.body = body
        self.identifier = token.string
        self.type_token = type_token

class ReturnNode(StatementNode):
    def __init__(self, token: Token, value: ExpressionNode | None, parser: "Parser"):
        super().__init__(token, [value], parser)
        self.value = value

class IfNode(StatementNode):
    def __init__(self, token: Token, condition: ExpressionNode, body: CodeBlockNode, else_body: CodeBlockNode | None, parser: "Parser"):
        super().__init__(token, [condition, body, else_body], parser)
        self.condition = condition
        self.body = body
        self.else_body = else_body

class WhileNode(StatementNode):
    def __init__(self, token: Token, condition: ExpressionNode, body: CodeBlockNode, parser: "Parser"):
        super().__init__(token, [condition, body], parser)
        self.condition = condition
        self.body = body

class ForNode(StatementNode):
    def __init__(self, token: Token, initialization: StatementNode, condition: ExpressionNode, increment: StatementNode, body: CodeBlockNode, parser: "Parser"):
        super().__init__(token, [initialization, condition, increment, body], parser)
        self.initialization = initialization
        self.condition = condition
        self.increment = increment
        self.body = body

class FunctionCallStatementNode(StatementNode):
    def __init__(self, token: Token, arguments: list[ExpressionNode], parser: "Parser"):
        super().__init__(token, arguments, parser)
        self.arguments = arguments

    def register(self) -> None:
        self.scope.resolve_symbol(self.token).reference(self)

class BreakNode(StatementNode):
    pass

class ContinueNode(StatementNode):
    pass

class PassNode(StatementNode):
    pass

class AssemblyNode(StatementNode):
    
    def __init__(self, token: Token, code: list[Token], parser: "Parser"):
        super().__init__(token, [], parser)
        self.code = code
        self.code_string = " ".join([token.string for token in code])