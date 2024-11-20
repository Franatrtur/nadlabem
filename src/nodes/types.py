from ..tokenizer.symbols import (IntToken, BoolToken, CharToken, Token, VoidToken,
                                 NumberToken, StringLiteralToken, BoolLiteralToken)
from typing import Type
from ..errors import TypeError
from ..tree import Node

class ExpressionType:
    def matches(self, other: ExpressionType) -> bool:
        pass
    @classmethod
    def match(cls, other: ExpressionType) -> bool:
        return isinstance(other, cls)

class NoType(ExpressionType):
    def __init__(self, name: int):
        self.name = name

    def matches(self, other: ExpressionType) -> bool:
        return isinstance(other, self.__class__)
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"
    def __str__(self):
        return self.name

Void = NoType(VoidToken.literal_string)

class ValueType(ExpressionType):
    def __init__(self, name: int):
        self.name = name

    def matches(self, other: ExpressionType) -> bool:
        return isinstance(other, self.__class__)
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"
    def __str__(self):
        return self.name

Int = ValueType(IntToken.literal_string)
Bool = ValueType(BoolToken.literal_string)
Char = ValueType(CharToken.literal_string)

#Void = ValueType(VoidToken.literal_string)

class Array(ExpressionType):
    def __init__(self, base_type: ExpressionType, size: int | None):
        self.base_type: ExpressionType = base_type
        self.size: int | None = size

    def matches(self, other: ExpressionType) -> bool:
        return isinstance(other, Array) and self.base_type.matches(other.base_type) and (self.size == other.size or self.size is None or other.size is None)
        
    def __repr__(self):
        nested = ", ".join(repr(nested) for nested in self.nested_types)
        return f"{self.__class__.__name__}({nested}, size={self.size})"
    def __str__(self):
        size = f"{self.size}" if self.size is not None else ""
        return f"{str(self.base_type)}[{size}]"


######################################################

class DeclarationType:
    pass

class VariableType(DeclarationType):
    def __init__(self, type: ExpressionType, is_reference: bool):
        self.expression_type: ExpressionType = type
        self.is_reference: bool = is_reference
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.expression_type}, is_reference={self.is_reference})"
    def __str__(self):
        return f"{str(self.expression_type)}{'*' if self.is_reference else ''}"


class FunctionType(DeclarationType):
    def __init__(self, return_type: ValueType | NoType, parameters: list[VariableType]):
        self.return_type: ValueType | NoType = return_type
        self.parameters: list[VariableType] = parameters

    def __repr__(self):
        parameters = ", ".join(repr(parameter) for parameter in self.parameters)
        return f"{self.__class__.__name__}({self.return_type}, [{parameters}])"
    def __str__(self):
        parameters = ", ".join(str(parameter) for parameter in self.parameters)
        return f"{str(self.return_type)} ({parameters})"







