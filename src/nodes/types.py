from ..tokenizer.symbols import (IntToken, UIntToken, StringToken, BoolToken, CharToken, ArrayToken, Token,
                                IntegerLiteralToken, VoidToken)
from typing import Type

class ValueType:
    """Base class for types."""
    def __init__(self, is_reference: bool = False, is_pointer: Union["ValueType", None] = None):
        #TODO: is_pointer is only for ints
        self.is_reference = is_reference
        self.is_pointer = is_pointer

    def matches(self, other: "ValueType", strict: bool = False) -> bool:
        if str(self) != str(other):
            return False
        return not strict or (self.is_const == other.is_const and self.is_volatile == other.is_volatile)

    @classmethod
    def any(cls, *classes: list[Type["ValueType"]], class_name = "CombinedType") -> Type["ValueType"]:
        """Returns a new class that matches any of the given classes."""
        return type(class_name, (ValueType,), {
            "matches": staticmethod(lambda self, other: any(cls.matches(other) for cls in classes))
        })

    def __str__(self):
        qualifiers = []
        if self.is_reference:
            qualifiers.append("*")
        return f"Type({' '.join(qualifiers)} {self.name})"

class Int(ValueType):
    name = IntToken.literal_string

class UInt(ValueType):
    name = UIntToken.literal_string

class Char(ValueType):
    name = CharToken.literal_string

class String(ValueType):
    name = StringToken.literal_string

class Bool(ValueType):
    name = BoolToken.literal_string

class Void(ValueType):
    name = VoidToken.literal_string


class Pointer(ValueType):
    """Represents a pointer to another type."""
    def __init__(self, base_type: ValueType, is_const: bool = False, is_volatile: bool = False):
        super().__init__(base_type.name, is_const, is_volatile)
        self.base_type = base_type

    def __str__(self):
        return super().__str__() + "*"


class Array(ValueType):
    """Represents an array of another type."""
    def __init__(self, base_type: ValueType, size: int = None):
        super().__init__(base_type.name)
        self.base_type = base_type
        self.size = size

    def __str__(self):
        size_str = f"[{self.size}]" if self.size is not None else "[]"
        return f"{self.base_type}{size_str}"


# class Struct(ValueType):
#     """Represents a C struct type."""
#     def __init__(self, name: str, fields: dict[str, ValueType]):
#         super().__init__(name)
#         self.fields = fields

#     def __str__(self):
#         fields_str = "; ".join(f"{type_} {name}" for name, type_ in self.fields.items())
#         return f"struct {self.name} {{ {fields_str}; }}"


class Function(ValueType):
    """Represents a function type."""
    def __init__(self, return_type: ValueType, parameters: list[ValueType]):
        super().__init__(return_type.name)
        self.return_type = return_type
        self.parameters = parameters

    def __str__(self):
        params_str = ", ".join(str(param) for param in self.parameters)
        return f"{self.return_type}({params_str})"

TYPES: dict[Type[Token], Type[ValueType]] = {
    IntToken: Int,
    UIntToken: UInt,
    CharToken: Char,
    StringToken: String,
    BoolToken: Bool,
    VoidToken: Void,
}

