from ..tokenizer.symbols import (IntToken, BoolToken, CharToken, Token, VoidToken, LiteralToken,
                                 CharLiteralToken, NumberToken, StringLiteralToken, BoolLiteralToken)
from typing import Type
from ..errors import TypeError
from ..tree import Node

class ExpressionType:
    def matches(self, other: "ExpressionType", strict: bool = False) -> bool:
        pass
    @classmethod
    def match(cls, other: "ExpressionType") -> bool:
        return isinstance(other, cls)

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



class NoType(ExpressionType):
    def __init__(self, name: int):
        self.name = name
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"
    def __str__(self):
        return self.name

Void = NoType(VoidToken.literal_string)

class ValueType(ExpressionType):
    def __init__(self, name: int):
        self.name = name

    def matches(self, other: ExpressionType, strict: bool = False) -> bool:
        return other in CompatibilityTable[self] if not strict else other == self
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"
    def __str__(self):
        return self.name

Int = ValueType(IntToken.literal_string)
Bool = ValueType(BoolToken.literal_string)
Char = ValueType(CharToken.literal_string)

CompatibilityTable: dict[ValueType, set[ValueType]] = {
    Int: [Int, Char],
    Char: [Int, Char],
    Bool: [Bool]
}

class Array(ExpressionType):
    def __init__(self, element_type: ExpressionType, size: int | None):
        self.element_type: ExpressionType = element_type
        self.size: int | None = size

    def matches(self, other: ExpressionType, strict: bool = False) -> bool:
        if self.size is None and other.size is not None:
            self.size = other.size
        if not strict:
            self.size = other.size = max(self.size, other.size)
        return isinstance(other, Array) and self.element_type.matches(other.element_type, strict=strict) and (self.size >= other.size)

    def size_defined(self) -> bool:
        if self.size is None:
            return False
        if isinstance(self.element_type, Array):
            return self.element_type.size_defined()
        return True
        
    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.element_type)}, size={self.size})"
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

    def matches(self, expression_type: ExpressionType, strict: bool = False) -> bool:
        if self.is_reference:
            return expression_type == Int
        return self.expression_type.matches(expression_type, strict=strict)
    
    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.expression_type)}, is_reference={self.is_reference})"
    def __str__(self):
        return f"{str(self.expression_type)}{'*' if self.is_reference else ''}"


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
        return f"{str(self.return_type)} ({parameters})"


VALUE_TYPES: dict[Type[Token], ExpressionType] = {
    IntToken: Int,
    BoolToken: Bool,
    CharToken: Char
}

RETURNABLE_TYPES: dict[Type[Token], ExpressionType] = {
    IntToken: Int,
    BoolToken: Bool,
    CharToken: Char,
    VoidToken: Void
}