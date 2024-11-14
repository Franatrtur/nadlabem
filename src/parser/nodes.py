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
        
    def link(self, parent: "AbstractSyntaxTreeNode"):
        self.parent: AbstractSyntaxTreeNode = parent
        self.scope: Context = parent.context
        if self.context is None:
            self.context = self.scope
        for child in self.children:
            child.add_parent(self)

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


ASTNode = AbstractSyntaxTreeNode

class ExpressionNode(AbstractSyntaxTreeNode):
    def __init__(self, token: Token, children: list[ASTNode], parser: "Parser"):
        super().__init__(token, children, parser)
        self.type: ValueType

class FunctionCallNode(ExpressionNode):
    def __init__(self, token: Token, arguments: list[ASTNode], parser: "Parser"):
        super().__init__(token, arguments, parser)

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

class LiteralNode(ExpressionNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

class ArrayLiteralNode(ExpressionNode):
    def __init__(self, token: Token, elements: list[ASTNode], parser: "Parser"):
        super().__init__(token, elements, parser)
        self.elements = elements

class IndexRetrievalNode(UnaryOperationNode):
    def __init__(self, token: Token, child: ASTNode, parser: "Parser"):
        super().__init__(token, child, parser)


class StatementNode(AbstractSyntaxTreeNode):
    pass

class CodeBlockNode(StatementNode):
    def __init__(self, token: Token, children: list[StatementNode], parser: "Parser"):
        super().__init__(token, children, parser)
        self.statements = children

class VariableDeclarationNode(StatementNode):
    def __init__(self, token: Token, value: ExpressionNode, type: ValueType | None, parser: "Parser"):
        super().__init__(token, [value], parser)
        self.value = value
        self.identifier = token.string
        self.type = type

class AssignmentNode(StatementNode):
    def __init__(self, token: Token, value: ExpressionNode, parser: "Parser"):
        super().__init__(token, [value], parser)
        self.value = value

class FunctionDeclarationNode(StatementNode):
    def __init__(self, token: Token, arguments: list[Token], body: CodeBlockNode, type: ValueType | None, parser: "Parser"):
        super().__init__(token, [body], parser)
        self.arguments = arguments
        self.body = body
        self.identifier = token.string
        self.type = type

class ArgumentDeclarationNode(StatementNode):
    def __init__(self, token: Token, type: ValueType | None, parser: "Parser"):
        super().__init__(token, [], parser)
        self.identifier = token.string
        self.type = type

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

class BreakNode(StatementNode):
    pass

class ContinueNode(StatementNode):
    pass

class PassNode(StatementNode):
    pass

class ProgramNode(AbstractSyntaxTreeNode):
    pass

