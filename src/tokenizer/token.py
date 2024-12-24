import re, ast
from typing import Type
from ..errors import SymbolError, NadLabemError
from pathlib import Path


class Token:
    def __init__(self, string: str, line: "Line"):
        self.string = string
        self.line = line

    def __str__(self):
        return f"{self.__class__.__name__}({repr(self.string)}, {self.line.brief})"
    
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
            "match": classmethod(lambda cls, token: any(cls.match(token) for cls in classes)),
            "_component_classes": classes  # Store component classes for subclass detection
        })

    @classmethod
    def detects_subclass(cls, other_cls: Type['Token']) -> bool:
        """
        Check if this token class can detect instances of the other token class.
        Works with classes generated through Token.any().
        
        Args:
            other_cls: The token class to check against
            
        Returns:
            bool: True if this class can detect instances of other_cls
        """
        # If this is a combined token (created by any()), check component classes
        if hasattr(cls, '_component_classes'):
            return any(c.detects_subclass(other_cls) for c in cls._component_classes)
            
        # For literal tokens or regular subclasses, check if detect() works on the other class's literal
        if hasattr(other_cls, 'literal_string'):
            return cls.detect(other_cls.literal_string)
            
        # For other cases, try to determine relationship through direct method comparison
        return (cls.detect == other_cls.detect) or (
            hasattr(other_cls, 'detect') and 
            all(cls.detect(s) for s in ['test_string'] if other_cls.detect(s))
        )


class Line:
    
    def __init__(self, string: str, number: int, location: Path | None = None):
        self.string = string
        self.number = number
        self.tokens: list[Token] = []
        self.comment: str = ""
        self.location: Path | None = location
        self.file: str = f"File \"{self.location}\"" if self.location is not None else "Anonymous file"

    @property
    def brief(self) -> str:
        return f"{self.location}:{self.number}"

    def __str__(self):
        return f"Line {self.number}: \n{repr(self.string.strip())}\n{self.file}, line {self.number}"
    def __repr__(self):
        return f"Line({self.brief}): {repr(self.string.strip())}"# [{tokens_string}]"
