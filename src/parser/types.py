from .parsing import Parser
from ..tokenizer.symbols import (Token, TypeToken, StarToken, ArrayBeginToken, ArrayEndToken, NumberToken,
                        CharToken, IntToken, BoolToken, VoidToken, AtToken)
from typing import Type
from ..nodes.types import VALUE_TYPES, RETURNABLE_TYPES, NoType, Int, Char, Bool, Void, Array, Pointer, VariableType, ExpressionType, ValueType
from ..errors import TypeError


class TypeParser(Parser):

    def value_type(self) -> ValueType:
        token = self.look_ahead()
        result: ExpressionType = self.expression_type()

        if not isinstance(result, ValueType):
            raise TypeError("Expected a value type, but got a complex expression type", token.line, allowed=VALUE_TYPES)

        return result


    def expression_type(self) -> ExpressionType:
        type_token = self.devour(TypeToken)
        result: ValueType = None

        for token_type, value_type in VALUE_TYPES.items():
            if token_type.match(type_token):
                result = value_type
                break

        while self.is_ahead(StarToken):
            self.devour(StarToken)
            result = Pointer(result)

        #handle arrays
        if self.is_ahead(ArrayBeginToken):
            self.devour(ArrayBeginToken)
            array_length = None
            if not self.is_ahead(ArrayEndToken):
                array_length = self.devour(NumberToken).value

            self.devour(ArrayEndToken)
            result = Array(result, size=array_length)

        #handle pointers once more
        if self.is_ahead(StarToken):
            self.devour(StarToken)
            result = Pointer(result)

        return result

    
    def return_type(self) -> ValueType | NoType:
        if self.is_ahead(VoidToken):
            self.devour(VoidToken)
            return Void
        else:
            return self.value_type()

    
    def variable_type(self) -> VariableType:
        #handle references
        is_ref: bool = False
        if self.is_ahead(AtToken):
            self.devour(AtToken)
            is_ref = True

        return VariableType(self.expression_type(), is_ref)