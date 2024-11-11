from ..tree import Node
from ..tokenizer import Token
from .scope import Context
from typing import Type
from .types import ValueType, LITERALS

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
                connector = connector if not (is_last_child and row_index > 0) else ""
                self_str += f"\n    {connector}{row}"
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
        self.arguments = arguments
        self.function_name: str = token.string

class BinaryOperationNode(ExpressionNode):
    def __init__(self, token: Token, left: ASTNode, right: ASTNode, parser: "Parser"):
        super().__init__(token, [left, right], parser)
        self.left = left
        self.operation: str = token.string
        self.right = right

class UnaryOperationNode(ExpressionNode):
    def __init__(self, token: Token, child: ASTNode, parser: "Parser"):
        super().__init__(token, [child], parser)
        self.child = child
        self.operation: str = token.string

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
        self.type = LITERALS[token.__class__]

class IndexRetrievalNode(UnaryOperationNode):
    def __init__(self, token: Token, child: ASTNode, parser: "Parser"):
        super().__init__(token, child, parser)


class StatementNode(AbstractSyntaxTreeNode):
    pass

class BlockNode(StatementNode):
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
    def __init__(self, token: Token, arguments: list[Token], body: BlockNode, parser: "Parser"):
        super().__init__(token, [body], parser)
        self.arguments = arguments
        self.body = body
        self.identifier = token.string

class ReturnNode(StatementNode):
    def __init__(self, token: Token, value: ExpressionNode | None, parser: "Parser"):
        super().__init__(token, [value], parser)
        self.value = value

class IfNode(StatementNode):
    def __init__(self, token: Token, condition: ExpressionNode, body: BlockNode, else_body: BlockNode | None, parser: "Parser"):
        super().__init__(token, [condition, body, else_body], parser)
        self.condition = condition
        self.body = body
        self.else_body = else_body

class WhileNode(StatementNode):
    def __init__(self, token: Token, condition: ExpressionNode, body: BlockNode, parser: "Parser"):
        super().__init__(token, [condition, body], parser)
        self.condition = condition
        self.body = body

class ForNode(StatementNode):
    def __init__(self, token: Token, iterator: Token, iterable: ExpressionNode, body: BlockNode, parser: "Parser"):
        super().__init__(token, [iterator, iterable, body], parser)
        self.iterator = iterator
        self.iterable = iterable
        self.body = body

class LoopStatementNode(StatementNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

class BreakNode(LoopStatementNode):
    pass

class ContinueNode(LoopStatementNode):
    pass

class ProgramNode(BlockNode):
    pass

