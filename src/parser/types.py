from .parsing import Parser
from ..tokenizer import (Token, TypeToken, StarToken, ArrayBeginToken, ArrayEndToken, NumberToken)
from typing import Type
from ..nodes.types import VALUE_TYPES, RETURNABLE_TYPES, Int, Char, Bool, Void, Array, VariableType, ExpressionType
from ..errors import TypeError

class VariableTypeParser(Parser):

    def parse(self) -> VariableType:

        type_token = self.devour(TypeToken)
        expr_type: ExpressionType

        for token_type, value_type in VALUE_TYPES.items():
            if token_type.match(type_token):
                expr_type = value_type
                break  # Exit the loop if a match is found, break will skip the following else:
        else:
            allowed = ", ".join(str(t) for t in VALUE_TYPES.values())
            raise TypeError(
                f"Cannot assign to type {type_token.string}, expected a value type", type_token.line,
                value_types=allowed, suggestion="Did you forget \"def\" to define a void function?"
            )

        while self.is_ahead(ArrayBeginToken):
            self.devour(ArrayBeginToken)
            
            array_length = None
            if not self.is_ahead(ArrayEndToken):
                array_length = self.devour(NumberToken).value

            self.devour(ArrayEndToken)
            expr_type = Array(expr_type, size=array_length)

        is_reference: bool = False
        if self.is_ahead(StarToken):
            self.devour(StarToken)
            is_reference = True

        return VariableType(expr_type, is_reference)


class ReturnTypeParser(Parser):

    def parse(self) -> ExpressionType:

        type_token = self.devour(TypeToken)

        for token_type, value_type in RETURNABLE_TYPES.items():
            if token_type.match(type_token):
                return value_type
        else:
            allowed = ", ".join(t.__name__ for t in RETURNABLE_TYPES.keys())
            raise TypeError(
                f"Cannot return type {type_token}", type_token.line,
                returnable_types=allowed
            )