from ..tree import Node
from ..tokenizer import Token, TypeToken, NameToken
from .scope import Context, Symbol, Namespace
from typing import Type
from .types import VariableType, FunctionType, Void, Int, Char, Bool, Array, DeclarationType, ExpressionType, ValueType, Comparator
from .node import AbstractSyntaxTreeNode as ASTNode
from .expression import ExpressionNode
from ..errors import TypeError, NameError

class StatementNode(ASTNode):
    pass

class CodeBlockNode(StatementNode):
    pass
    #def register_children(self):
        # do the whole layer before nested layers, except blocks in blocks
        # for child in self.children:
        #     child.register()
        # for child in self.children:
        #     child.register_children()
        # for child in self.children:
        #     child.verify()


class ModuleNode(StatementNode):
    def __init__(self, token: Token, name_token: NameToken | None, children: list[StatementNode], parser: "Parser"):
        super().__init__(token, children, parser)
        self.context = Namespace(self, parent=self.scope)
        self.name_token: NameToken | None = name_token
    
    def register(self) -> None:
        if not isinstance(self.scope, Namespace):
            raise NameError(f"Illegal module declaration outside of a namespace", self.token.line, suggestion="Modules cannot be declared inside functions")
        self.scope.relate(self.name_token, self.context)


class IncludeNode(StatementNode):
    def __init__(self, token: Token, name_token: NameToken | None, context_to_link: Namespace, parser: "Parser"):
        super().__init__(token, [], parser)
        self.context = context_to_link
        self.name_token: NameToken | None = name_token
    
    def register(self) -> None:
        if not isinstance(self.scope, Namespace):
            raise NameError(f"Illegal include outside of a namespace", self.token.line, suggestion="Includes cannot be declared inside functions")
        self.scope.relate(self.name_token, self.context)

    def prune(self) -> bool:
        return True     # our work is done
    


class VariableDeclarationNode(StatementNode):
    def __init__(self, name: Token, expression_value: ExpressionNode, var_type: VariableType, parser: "Parser"):
        super().__init__(name, [expression_value], parser)
        self.assignment: ExpressionNode = expression_value
        self.name_token = name
        self.node_type: VariableType = var_type
        self.by_reference: bool = var_type.is_reference

    def register(self) -> None:
        self.symbol = Symbol(self.name_token, node=self)
        self.context.register_symbol(self.symbol)

    def prune(self) -> bool:
        return not self.symbol.is_relevant

    def verify(self) -> None:
        if self.by_reference:
            Comparator.pointer_assignment(self.node_type, self.assignment.node_type, node=self)
        else:
            Comparator.assignment(self.node_type, self.assignment.node_type, node=self)

class ArgumentDeclarationNode(StatementNode):
    def __init__(self, name_token: Token, var_type: VariableType, parser: "Parser"):
        super().__init__(name_token, [], parser)
        self.name_token = name_token
        self.node_type: VariableType = var_type

    def prune(self) -> bool:
        return not self.symbol.is_relevant

    def register(self) -> None:
        symbol = Symbol(self.name_token, node=self)
        self.symbol: Symbol = symbol
        self.context.register_symbol(symbol)

class AssignmentNode(StatementNode):
    def __init__(self, name_token: Token, value: ExpressionNode, index: ExpressionNode | None, by_reference: bool, parser: "Parser"):
        super().__init__(name_token, [value] + ([index] if index else []), parser)
        self.value: ExpressionNode = value
        self.by_reference: bool = by_reference
        self.index: ExpressionNode | None = index

    def register(self) -> None:
        symbol = self.scope.get_symbol(self.token)
        self.symbol = symbol
        self.variable: VariableDeclarationNode = symbol.node
        symbol.reference(self)

    def verify(self) -> None:
        if self.index is not None:
            Comparator.array_index_assignment(self.variable.node_type, self.index.node_type, self.value.node_type, node=self)
        elif self.by_reference:
            Comparator.pointer_assignment(self.variable.node_type, self.value.node_type, node=self)
        else:
            Comparator.assignment(self.variable.node_type, self.value.node_type, node=self)

class IncrementalNode(StatementNode):
    def __init__(self, token: Token, name_token: NameToken, parser: "Parser"):
        super().__init__(token, [], parser)
        self.name_token: NameToken = name_token

    def register(self) -> None:
        self.symbol: Symbol = self.scope.get_symbol(self.name_token)
        self.symbol.reference(self)
        var_type: VariableType = self.symbol.node.node_type
        Comparator.increment(var_type, node=self)


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
        self.symbol: Symbol = Symbol(self.name_token, node=self)
        self.scope.register_symbol(self.symbol)

    def prune(self) -> bool:
        return not self.symbol.is_relevant

    def verify(self) -> None:
        if not self.return_nodes and self.node_type.return_type is not Void:
            self.config.warn(TypeError(f"Function \"{self.name_token.string}\" has no return statement", self.token.line))

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
        Comparator.return_value(value_type, function_type, node=self)
        self.function.return_nodes.append(self)


class IfNode(StatementNode):
    def __init__(self, token: Token, condition: ExpressionNode, body: CodeBlockNode, else_body: CodeBlockNode | None, parser: "Parser"):
        children = [condition, body] if else_body is None else [condition, body, else_body]
        super().__init__(token, children, parser)
        self.condition: ExpressionNode = condition
        self.body: StatementNode = body
        self.else_body: StatementNode | None = else_body

    def verify(self) -> None:
        Comparator.condition(self.condition.node_type, node=self)


class WhileNode(StatementNode):
    def __init__(self, token: Token, condition: ExpressionNode, body: CodeBlockNode, parser: "Parser"):
        super().__init__(token, [condition, body], parser)
        self.condition = condition
        self.body = body

    def verify(self) -> None:
        Comparator.condition(self.condition.node_type, node=self)

class ForNode(StatementNode):
    def __init__(self, token: Token, initialization: StatementNode, condition: ExpressionNode, increment: StatementNode, body: CodeBlockNode, parser: "Parser"):
        super().__init__(token, [initialization, condition, body, increment], parser)
        self.initialization = initialization
        self.condition = condition
        self.increment = increment
        self.body = body

    def verify(self) -> None:
        Comparator.condition(self.condition.node_type, node=self)

class LoopNode(StatementNode):
    def __init__(self, token: Token, count: ExpressionNode, body: CodeBlockNode, parser: "Parser"):
        super().__init__(token, [count, body], parser)
        self.iterations: ExpressionNode = count
        self.body = body

class FunctionCallStatementNode(StatementNode):
    def __init__(self, token: Token, arguments: list[ExpressionNode], parser: "Parser"):
        super().__init__(token, arguments, parser)
        self.arguments: list[ExpressionNode] = arguments

    def register(self) -> None:
        self.symbol: Symbol = self.scope.get_symbol(self.token)
        self.symbol.reference(self)

    def verify(self) -> None:
        function_type: FunctionType = self.symbol.node.node_type
        Comparator.function_call_statement(function_type, [arg.node_type for arg in self.arguments], node=self)

class BreakNode(StatementNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

    def register(self) -> None:
        self.loop: ForNode | WhileNode = self.closest_parent(WhileNode, ForNode)
        if self.loop is None:
            raise SyntaxError("Break statement outside of loop", self.token.line)

class ContinueNode(StatementNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

    def register(self) -> None:
        self.loop: ForNode | WhileNode = self.closest_parent(WhileNode, ForNode)
        if self.loop is None:
            raise SyntaxError("Continue statement outside of loop", self.token.line)

class PassNode(StatementNode):
    def __init__(self, token: Token, parser: "Parser"):
        super().__init__(token, [], parser)

    def prune(self) -> bool:
        return True

class AssemblyNode(StatementNode):
    
    def __init__(self, token: Token, code: list[Token], parser: "Parser"):
        super().__init__(token, [], parser)
        self.code = code
        self.code_string = " ".join([token.string for token in code])