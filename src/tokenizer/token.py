import re, ast
from typing import Type
from ..errors import SymbolError, NadLabemError


class Token:

    def __init__(self, string: str, line: "Line"):
        self.string = string
        self.line = line

    def __str__(self):
        return f"{self.__class__.__name__}(\"{self.string}\")"
    def __repr__(self):
        return str(self)

    @staticmethod
    def literal(string: str, class_name: str) -> Type['Token']:
        # Define a new subclass of Token with a custom detect method, case insensitive
        return type(class_name, (Token,), {
            "detect": staticmethod(lambda s: s.lower() == string.lower()),
            "literal_string": string
        })

    @classmethod
    def match(cls, token: 'Token') -> bool:
        # Checks if the token is exactly an instance of the calling class
        return isinstance(token, cls)

    @staticmethod
    def any(*classes: list[Type["Token"]], class_name: str = "CombinedToken") -> Type["Token"]:
        # Define a new subclass of Token with a custom detect method
        return type(class_name, (Token,), {
            "detect": staticmethod(lambda s: any(cls.detect(s) for cls in classes)),
            "match": classmethod(lambda cls, token: any(cls.match(token) for cls in classes))
        })


class Line:
    
    def __init__(self, string: str, number: int):
        self.string = string
        self.number = number
        self.tokens: list[Token] = []
        self.comment: str = ""

    def __str__(self):
        tokens_string = ','.join(map(str, self.tokens[:min(8, len(self.tokens))]))
        if len(self.tokens) > 8:
            tokens_string += ' . . . '
        return f"Line {self.number}: \"{self.string}\" [{tokens_string}]"
    def __repr__(self):
        return str(self)
