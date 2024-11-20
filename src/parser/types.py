from .parsing import Parser
from ..tokenizer import (Token, TypeToken, StarToken, ArrayBeginToken, ArrayEndToken, NumberToken)
from typing import Type
from ..nodes.types import TYPES, Int, Char, Bool, Void, ValueType, Array
from ..errors import TypeError

class TypeParser(Parser):

    def parse(self) -> ValueType:

        type_token = self.devour(TypeToken)
        result_type: ValueType
        
        for token_type, value_type in TYPES.items():
            if token_type.match(type_token):
                result_type = value_type()
                break  # Exit the loop if a match is found, break will skip the following else:
        else:
            raise TypeError(f"Unsupported type {type_token.string}", type_token.line)
        
        while self.is_ahead(ArrayBeginToken):
            self.devour(ArrayBeginToken)
            array_length: int = self.devour(NumberToken).value
            self.devour(ArrayEndToken)
            result_type = Array(result_type, size=array_length)

        if self.is_ahead(StarToken):
            self.devour(StarToken)
            result_type.is_reference = True

        return result_type
