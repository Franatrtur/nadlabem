from ..tokenizer.symbols import (IntToken, BoolToken, CharToken, Token, VoidToken, LiteralToken, LogicalNotToken,
                                 CharLiteralToken, NumberToken, StringLiteralToken, BoolLiteralToken, DoubleToken)
from typing import Type
from ..errors import TypeError
from ..tree import Node
from .node import AbstractSyntaxTreeNode as ASTNode

class NadLabemType:
    pass


class NoType(NadLabemType):
    def __init__(self, name: int):
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"
    def __str__(self):
        return self.name

Void = NoType(VoidToken.literal_string)

class ExpressionType(NadLabemType):

    @staticmethod
    def decide(token: Token) -> "ExpressionType":
        if NumberToken.match(token):
            return Int
        elif BoolLiteralToken.match(token):
            return Bool
        elif CharLiteralToken.match(token):
            return Char
        elif StringLiteralToken.match(token):
            return Array(Char, size=len(token.bytes))
        else:
            raise TypeError(f"Cannot decide literal expression type of \"{token}\"", token.line)


class ValueType(ExpressionType):
    def __init__(self, name: int):
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"
    def __str__(self):
        return self.name

Int = ValueType(IntToken.literal_string)
Bool = ValueType(BoolToken.literal_string)
Char = ValueType(CharToken.literal_string)
Double = ValueType(DoubleToken.literal_string)


class Pointer(ValueType):
    def __init__(self, element_type: ExpressionType):
        self.element_type: ExpressionType = element_type

    def __repr__(self):
        return f"Pointer({repr(self.element_type)})"
    def __str__(self):
        return str(self.element_type) + "*"


class Array(ExpressionType):
    def __init__(self, element_type: ValueType, size: int | None):
        self.element_type: ValueType = element_type
        self.size: int | None = size
        
    def __repr__(self):
        return f"Array({repr(self.element_type)}, size={self.size})"
    def __str__(self):
        size = f"{self.size}" if self.size is not None else ""
        return f"{str(self.element_type)}[{size}]"


######################################################

class DeclarationType:
    @classmethod
    def match(cls, other: "ExpressionType") -> bool:
        return isinstance(other, cls)

class VariableType(DeclarationType):
    def __init__(self, expression_type: ExpressionType, is_reference: bool):
        self.expression_type: ExpressionType = expression_type
        self.is_reference: bool = is_reference
    
    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.expression_type)}, is_reference={self.is_reference})"
    def __str__(self):
        return f"{'@' if self.is_reference else ''}{str(self.expression_type)}"


class FunctionType(DeclarationType):
    def __init__(self, return_type: ValueType | NoType, parameters: list[VariableType]):
        self.return_type: ValueType | NoType = return_type
        self.parameters: list[VariableType] = parameters

    def match_params(self, parameters: list[ExpressionType]) -> bool:
        if len(self.parameters) != len(parameters):
            return False
        for i in range(len(self.parameters)):
            if not self.parameters[i].matches(parameters[i]):
                return False
        return True

    def __repr__(self):
        parameters = ", ".join(repr(parameter) for parameter in self.parameters)
        return f"{self.__class__.__name__}({self.return_type}, [{parameters}])"
    def __str__(self):
        parameters = ", ".join(str(parameter) for parameter in self.parameters)
        return f"({parameters}) -> {self.return_type}"


VALUE_TYPES: dict[Type[Token], ValueType] = {
    IntToken: Int,
    BoolToken: Bool,
    CharToken: Char,
    DoubleToken: Double,
}

RETURNABLE_TYPES: dict[Type[Token], NadLabemType] = {
    IntToken: Int,
    BoolToken: Bool,
    CharToken: Char,
    VoidToken: Void,
    DoubleToken: Double,
}


class Comparator:

    @staticmethod
    def match(left: ValueType, right: ValueType) -> bool:
        return (left is right or
            (isinstance(left, Pointer) and
            isinstance(right, Pointer) and
            Comparator.match(left.element_type, right.element_type)) or
            (isinstance(left, Array) and
            isinstance(right, Array) and
            Comparator.match(left.element_type, right.element_type)))

    def cast(from_type: ExpressionType, to_type: ValueType, node: ASTNode) -> ValueType:
        if not isinstance(from_type, ValueType) or not isinstance(to_type, ValueType):
            raise TypeError(f"Cannot cast {from_type} to {to_type}", node.token.line)
        if isinstance(to_type, Pointer):
            node.config.warn(TypeError(f"Pointer casting is dangerous", node.token.line))
        if from_type is to_type:
            node.config.warn(TypeError(f"Casting {from_type} to {to_type} is pointless", node.token.line))
        return to_type

    @staticmethod
    def _binary_operation(left: ValueType, right: ValueType, allowed: set[ValueType], node: ASTNode) -> None:
        if not isinstance(left, ValueType) or not isinstance(right, ValueType) or left is not right:
            raise TypeError(f"Cannot perform binary operation {node.token.string} on types {left} and {right}", node.token.line, allowed=allowed)

    @staticmethod
    def comparison(left: ExpressionType, right: ExpressionType, node: ASTNode) -> ValueType:
        Comparator._binary_operation(left, right, allowed = {Int, Char, Double}, node=node)
        return Bool

    @staticmethod
    def logic(left: ExpressionType, right: ExpressionType, node: ASTNode) -> ValueType:
        Comparator._binary_operation(left, right, allowed = {Bool}, node=node)
        return Bool

    @staticmethod
    def arithmetic(left: ExpressionType, right: ExpressionType, node: ASTNode) -> ValueType:
        Comparator._binary_operation(left, right, allowed = {Int, Char, Double}, node=node)
        return left

    @staticmethod
    def pointer_access(source: VariableType, node: ASTNode) -> ValueType:
        return Pointer(source.expression_type)

    @staticmethod
    def dereference(source: VariableType, node: ASTNode) -> ValueType:
        if not isinstance(source.expression_type, Pointer):
            raise TypeError(f"Cannot dereference non-pointer type {source.expression_type}", node.token.line)
        if isinstance(source.expression_type.element_type, Array):
            raise TypeError(f"Cannot dereference array (from pointer type {source.expression_type})", node.token.line)
        return source.expression_type.element_type

    @staticmethod
    def unary_logic(operand: ExpressionType, node: ASTNode) -> ValueType:
        if operand is not Bool:
            raise TypeError(f"Cannot perform unary logical operation on type {operand}", node.token.line)
        return Bool
    
    @staticmethod
    def unary_arithmetic(operand: ExpressionType, node: ASTNode) -> ValueType:
        if operand not in {Int, Char, Double}:
            raise TypeError(f"Cannot perform unary arithmetic operation on type {operand}", node.token.line)
        return operand

    @staticmethod
    def function_call_value(function: FunctionType, arguments: list[ExpressionType], node: ASTNode) -> ValueType:
        if function.return_type is Void:
            raise TypeError(f"Function \"{node.symbol.name}\" does not return a value", node.token.line)
        Comparator.function_call(function, arguments, node)
        return function.return_type


    @staticmethod
    def function_call(function_type: FunctionType, arguments: list[ExpressionType], node: ASTNode) -> None:
        if len(function_type.parameters) != len(arguments):
            raise TypeError(f"Function \"{node.symbol.name}\" expects {len(function_type.parameters)} argument/s, but {len(arguments)} given", node.token.line)
        if not isinstance(function_type, FunctionType):
            raise TypeError(f"Cannot call \"{node.token.string}\" of type {function_type} as a function", node.token.line)
        for getting, giving in zip(function_type.parameters, arguments):
            if getting.is_reference:
                Comparator.pointer_assignment(getting, giving, node)
            else:
                if not Comparator.match(getting.expression_type, giving):
                    raise TypeError(f"Cannot assign type {giving} to {getting}", node.token.line)

    @staticmethod
    def function_call_statement(function_type: FunctionType, arguments: list[ExpressionType], node: ASTNode) -> None:
        Comparator.function_call(function_type, arguments, node)
        if function_type.return_type is not Void:
            node.config.warn(TypeError(f"Non-void return type {function_type.return_type} in function call statement, assign the return value to a variable", node.token.line))

    @staticmethod
    def variable_reference(var_type: VariableType,
                           load_pointer: bool,
                           dereference: bool,
                           index: ExpressionType | None,
                           node: ASTNode) -> ValueType:
        if index is not None:
            var_type = VariableType(Comparator.array_index_value(var_type, index, node), is_reference=False)
        if load_pointer:
            return Comparator.pointer_access(var_type, node)
        elif dereference:
            return Comparator.dereference(var_type, node)
        else:
            return var_type.expression_type

    @staticmethod
    def array_index_value(array: VariableType, index: ExpressionType, node: ASTNode) -> ValueType:
        Comparator.array_access(array.expression_type, index, node)
        return array.expression_type.element_type

    @staticmethod
    def assignment(left: VariableType, right: ExpressionType, node: ASTNode) -> None:
        if isinstance(right, Array):
            if not isinstance(left.expression_type, Array):
                raise TypeError(f"Cannot assign array to non-array variable", node.token.line)

            left: Array = left.expression_type
            right: Array

            if left.size is None:
                left.size = right.size
            if right.element_type is None:
                right.element_type = left.element_type

            if left.size is None:
                raise TypeError(f"Could not infer size of array", node.token.line)
            if not Comparator.match(left.element_type, right.element_type):
                raise TypeError(f"Cannot assign array type {right} to {left}", node.token.line)
            if left.size < right.size:
                raise TypeError(f"Cannot assign array of size {right.size} to array of size {left.size}", node.token.line)

        elif not Comparator.match(left.expression_type, right):
            raise TypeError(f"Cannot assign type {right} to {left} by value", node.token.line)

    @staticmethod
    def pointer_assignment(left: VariableType, right: ExpressionType, node: ASTNode) -> None:
        if not left.is_reference:
            raise TypeError(f"Cannot assign type by reference to non-reference type {left}", node.token.line)
        if not isinstance(right, Pointer):
            raise TypeError(f"Cannot assign non-pointer type {right} to {left} by reference", node.token.line)
        if not Comparator.match(left.expression_type, right.element_type):
            raise TypeError(f"Cannot assign type {right} to {left} by reference", node.token.line)

    @staticmethod
    def array_access(array_expr: ExpressionType, index: ExpressionType, node: ASTNode) -> None:
        if not isinstance(array_expr, Array):
            raise TypeError(f"Cannot index variable of type {array_expr} as an array", node.token.line)
        if index not in {Int, Char}:
            raise TypeError(f"Cannot index array with type {index}", node.token.line)

    @staticmethod
    def array_index_assignment(array: VariableType, index: ExpressionType, value: ExpressionType, node: ASTNode) -> None:
        Comparator.array_access(array.expression_type, index, node)
        #TODO: write with index and pointer support
        if not Comparator.match(array.expression_type.element_type, value):
            raise TypeError(f"Cannot assign type {value} to array of type {array.expression_type}", node.token.line)

    @staticmethod
    def return_value(value_type: ValueType | NoType, function_type: FunctionType, node: ASTNode) -> None:
        if value_type is not function_type.return_type:
            raise TypeError(f"Cannot return value of type {value_type} from function of type {function_type}", node.token.line)

    @staticmethod
    def condition(condition_type: ExpressionType, node: ASTNode) -> None:
        if condition_type is not Bool:
            raise TypeError(f"Expected bool type in condition, got type {condition_type}", node.token.line)

    @staticmethod
    def increment(var_type: VariableType, node: ASTNode) -> None:
        if var_type.expression_type not in {Char, Bool, Double}:
            raise TypeError(f"Cannot increment/decrement type {var_type.expression_type}", node.token.line, allowed={Char, Bool, Double})