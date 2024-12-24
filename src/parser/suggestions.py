from ..tokenizer.symbols import (Token, ArrayEndToken, CloseParenToken, TypeToken, NameToken, LiteralToken, UnaryToken)
from typing import Type
# here we will define dict: (expected_class, found_class): suggestion(text string)

SUGGESTIONS: dict[tuple[Type[Token], Type[Token]], str] = {

    # (a b) [a b] instead of (a,b) [a, b]
    (Token.any(ArrayEndToken, CloseParenToken), Token.any(TypeToken, NameToken, LiteralToken, UnaryToken)): 
    "Perhaps you forgot a comma? (,)",

    
}

#TODO: select suggestion based on the current parser as well

def find_suggestion(expected: Type[Token], got: Token, parser: "Parser") -> str | None:
    for (expected_class, got_class), suggestion in SUGGESTIONS.items():
        # if the expected class in in the tuple or is a subclass of any in the tuple
        if expected_class.detects_subclass(expected) and got_class.match(got):
            return SUGGESTIONS[(expected_class, got_class)]
    return None