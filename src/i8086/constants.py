# I8086 - SPECIFIC CONSTANTS

from ..nodes.types import Int, Char, S

TYPES: dict[Type[Token], Type[ValueType]] = {
    IntToken: Int,
    CharToken: Char,
    BoolToken: Bool,
    VoidToken: Void,
}