from ..tokenizer.symbols import (IntToken, UIntToken, StringToken, BoolToken, CharToken, ArrayToken, Token,
                                IntegerLiteralToken)
from typing import Type

class ValueType:

    def __init__(self, type_name: str):
        self.type_name = type_name

Int = ValueType(IntToken.literal_string)
UInt = ValueType(UIntToken.literal_string)
Char = ValueType(CharToken.literal_string)
String = ValueType(StringToken.literal_string)
Bool = ValueType(BoolToken.literal_string)
#ArrayType = ValueType(ArrayToken.literal_string)

LITERALS: dict[Type[Token], ValueType] = {
    IntToken: Int,
    UIntToken: UInt,
    CharToken: Char,
    StringToken: String,
    BoolToken: Bool,

    IntegerLiteralToken: Int,
}