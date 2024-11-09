import re, ast
from typing import Type
from .token import Token, Line
from ..errors import SymbolError


class IntegerLiteralToken(Token):
    def __init__(self, string: str, line: Line):
        super().__init__(string, line)
        try:
            self.value = ast.literal_eval(string)
        except SyntaxError as e:
            raise SymbolError("Invalid integer literal")
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.isnumeric() or re.match(r"^0x[0-9a-fA-F]+$", string)


class StringLiteralToken(Token):
    def __init__(self, string: str, line: Line):
        super().__init__(string, line)
        try:
            self.value = ast.literal_eval(string)
        except Exception as e:
            raise SymbolError("Invalid string literal")
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.startswith("\"") or string.startswith("'")


class CommentToken(Token):
    def __init__(self, string: str, line: Line):
        super().__init__(string, line)
        self.value = string[1:]
    @staticmethod
    def detect(string: str) -> bool:
        return string.startswith(";")


IfToken = Token.literal("if", "IfToken")
ElseToken = Token.literal("else", "ElseToken")
WhileToken = Token.literal("while", "WhileToken")
ForToken = Token.literal("for", "ForToken")

IntToken = Token.literal("int", "IntToken")
UIntToken = Token.literal("uint", "UIntToken")
FloatToken = Token.literal("float", "FloatToken")
StringToken = Token.literal("string", "StringToken")
BoolToken = Token.literal("bool", "BoolToken")

class NameToken(Token):
    @staticmethod
    def detect(string: str) -> bool:
        return string[0].isalpha()

IsEqualToken = Token.literal("==", "IsEqualToken")
IsNotEqualToken = Token.literal("!=", "IsNotEqualToken")
LessThanToken = Token.literal("<", "LessThanToken")
GreaterThanToken = Token.literal(">", "GreaterThanToken")
IsLtEqToken = Token.literal("<=", "IsLtEqToken")
IsGtEqToken = Token.literal(">=", "IsGtEqToken")

EqualsToken = Token.literal("=", "EqualsToken")
NegationToken = Token.literal("!", "NegationToken")

CommaToken = Token.literal(",", "CommaToken")
ColonToken = Token.literal(":", "ColonToken")
HashToken = Token.literal("#", "HashToken")

PlusToken = Token.literal("+", "PlusToken")
MinusToken = Token.literal("-", "MinusToken")
MultiplyToken = Token.literal("*", "MultiplyToken")
DivideToken = Token.literal("/", "DivideToken")

OpenParenToken = Token.literal("(", "OpenParenToken")
CloseParenToken = Token.literal(")", "CloseParenToken")

CodeBlockBeginToken = Token.literal("{", "CodeBlockBeginToken")
CodeBlockEndToken = Token.literal("}", "CodeBlockEndToken")

ArrayBeginToken = Token.literal("[", "ArrayBeginToken")
ArrayEndToken = Token.literal("]", "ArrayEndToken")

class IgnoreToken(Token):
    @staticmethod
    def detect(string: str) -> bool:
        return True

class NewLineToken(Token):
    pass


#order matters as priority is used for detection
TOKEN_DETECTORS = [
    IntegerLiteralToken,
    StringLiteralToken,
    CommentToken,

    IfToken,
    WhileToken,
    ElseToken,
    ForToken,

    IntToken,
    UIntToken,
    FloatToken,
    StringToken,
    BoolToken,

    NameToken,

    IsEqualToken,
    IsNotEqualToken,
    IsGtEqToken,
    IsLtEqToken,
    GreaterThanToken,
    LessThanToken,

    EqualsToken,
    NegationToken,

    CommaToken,
    ColonToken,
    HashToken,

    PlusToken,
    MinusToken,
    MultiplyToken,
    DivideToken,

    OpenParenToken,
    CloseParenToken,

    CodeBlockBeginToken,
    CodeBlockEndToken,

    ArrayBeginToken,
    ArrayEndToken,
]
