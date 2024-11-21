# I8086 - SPECIFIC CONSTANTS

from ..nodes.types import Int, Char, S

SIZE: dict[Type[Token], int] = {
    IntToken: 2,
    CharToken: 1,
    BoolToken: 1,
    VoidToken: 0,
}

def sizeof()