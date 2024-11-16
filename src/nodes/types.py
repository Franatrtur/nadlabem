from ..tokenizer.symbols import (IntToken, StringToken, BoolToken, CharToken, Token,
                                VoidToken)
from typing import Type

class ValueType:
    """Base class for types."""
    def __init__(self, original: bool = True):
        self.original = original

    @classmethod
    def match(cls, val_type: "ValueType"):
        return isinstance(cls, val_type)
    
    def matches(self, other: "ValueType") -> bool:
        return self.__class__.match(other)

    @classmethod
    def any(cls, *classes: list[Type["ValueType"]], class_name = "CombinedType") -> Type["ValueType"]:
        """Returns a new class that matches any of the given classes."""
        return type(class_name, (ValueType,), {
            "matches": staticmethod(lambda self, other: any(cls.matches(other) for cls in classes))
        })

    def __str__(self):
        return f"Type({self.name}{'' if self.original else '*'})"

class Int(ValueType):
    name = IntToken.literal_string

class Char(ValueType):
    name = CharToken.literal_string

class String(ValueType):
    name = StringToken.literal_string

class Bool(ValueType):
    name = BoolToken.literal_string

class Void(ValueType):
    name = VoidToken.literal_string


class Array(ValueType):
    """Represents an array of another type."""
    def __init__(self, base_type: ValueType, size: int = None):
        super().__init__(base_type.name)
        self.base_type = base_type
        self.size = size

    def __str__(self):
        size_str = f"[{self.size}]" if self.size is not None else "[]"
        return f"{self.base_type}{size_str}"


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
    CharToken: Char,
    StringToken: String,
    BoolToken: Bool,
    VoidToken: Void,
}

