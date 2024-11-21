import re, ast
from typing import Type
from .token import Token, Line
from ..errors import SymbolError


class NumberToken(Token):
    """Also represents one char"""
    def __init__(self, string: str, line: Line):
        super().__init__(string, line)
        try:
            self.value: int = ast.literal_eval(string)
        except SyntaxError as e:
            raise SymbolError("Invalid integer literal")

    @staticmethod
    def detect(string: str) -> bool:
        return string.isnumeric() or re.match(r"^0(x[0-9a-fA-F]+|o[0-7]+|b[01]+)$", string)


class CharLiteralToken(Token):
    def __init__(self, string: str, line: Line):
        super().__init__(string, line)
        try:
            evaled = ast.literal_eval(string)
        except Exception as e:
            raise SymbolError("Invalid char literal", line)

        if len(evaled) != 1:
            raise SymbolError("Char literal must be exactly one character", line)
        byte = bytes(evaled, encoding='utf8')
        if len(byte) != 1:
            raise SymbolError("Invalid ASCII character in char literal", line)
        self.value = int(byte[0])

    @staticmethod
    def detect(string: str) -> bool:
        return string.startswith("'")


class StringLiteralToken(Token):
    def __init__(self, string: str, line: Line):
        super().__init__(string, line)
        try:
            self.value = ast.literal_eval(string)
        except Exception as e:
            raise SymbolError("Invalid string literal", line)
        self.bytes: bytes = bytes(self.value, encoding='utf8')
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.startswith('"')


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
ReturnToken = Token.literal("return", "ReturnToken")
BreakToken = Token.literal("break", "BreakToken")
ContinueToken = Token.literal("continue", "ContinueToken")
PassToken = Token.literal("pass", "PassToken")
DefinitionToken = Token.literal("def", "DefinitionToken")

LogicalAndToken = Token.literal("and", "LogicalAndToken")
LogicalOrToken = Token.literal("or", "LogicalOrToken")
LogicalNotToken = Token.literal("not", "LogicalNotToken")

IntToken = Token.literal("int", "IntToken")
BoolToken = Token.literal("bool", "BoolToken")
CharToken = Token.literal("char", "CharToken")
VoidToken = Token.literal("void", "VoidToken")


class NameToken(Token):
    @staticmethod
    def detect(string: str) -> bool:
        return string[0].isalpha()

class BoolLiteralToken(Token):
    def __init__(self, string: str, line: Line):
        super().__init__(string, line)
        self.value = True if string.lower() == "true" else False

    @staticmethod
    def detect(string: str) -> bool:
        return string.lower() in ["true", "false"]

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

AmpersandToken = Token.literal("&", "AmpersandToken")
BinaryOrToken = Token.literal("|", "BinaryOrToken")
BinaryXorToken = Token.literal("^", "BinaryXorToken")
BinaryNotToken = Token.literal("~", "BinaryNotToken")

PlusToken = Token.literal("+", "PlusToken")
MinusToken = Token.literal("-", "MinusToken")
StarToken = Token.literal("*", "StarToken")
DivideToken = Token.literal("/", "DivideToken")
IntegerDivideToken = Token.literal("//", "IntegerDivideToken")
ModuloToken = Token.literal("%", "ModuloToken")

OpenParenToken = Token.literal("(", "OpenParenToken")
CloseParenToken = Token.literal(")", "CloseParenToken")

OpenBraceToken = Token.literal("{", "OpenBraceToken")
CloseBraceToken = Token.literal("}", "CloseBraceToken")

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
    NumberToken,
    CharLiteralToken,
    StringLiteralToken,
    CommentToken,

    BoolLiteralToken,

    IfToken,
    WhileToken,
    ElseToken,
    ForToken,
    ReturnToken,
    BreakToken,
    ContinueToken,
    PassToken,
    DefinitionToken,

    LogicalAndToken,
    LogicalOrToken,
    LogicalNotToken,

    IntToken,
    BoolToken,
    CharToken,
    VoidToken,

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

    AmpersandToken,
    BinaryOrToken,
    BinaryXorToken,
    BinaryNotToken,

    PlusToken,
    MinusToken,
    StarToken,
    DivideToken,
    IntegerDivideToken,
    ModuloToken,

    OpenParenToken,
    CloseParenToken,

    OpenBraceToken,
    CloseBraceToken,

    ArrayBeginToken,
    ArrayEndToken,
]


TypeToken = Token.any(
    IntToken,
    BoolToken,
    CharToken,
    VoidToken,
    class_name="TypeToken"
)

KeywordToken = Token.any(
    IfToken,
    WhileToken,
    ElseToken,
    ForToken,
    ReturnToken,
    BreakToken,
    ContinueToken,
    PassToken,
    DefinitionToken,
    class_name="KeywordToken"
)

StatementBeginToken = Token.any(
    KeywordToken,
    HashToken,
    TypeToken,
    class_name="StatementBeginToken"
)

LogicalToken = Token.any(
    LogicalAndToken,
    LogicalOrToken,
    LogicalNotToken,
    class_name="LogicalToken"
)

ComparisonToken = Token.any(
    IsEqualToken,
    IsNotEqualToken,
    IsGtEqToken,
    IsLtEqToken,
    GreaterThanToken,
    LessThanToken,
    class_name="ComparisonToken"
)

BinaryToken = Token.any(
    AmpersandToken,
    BinaryOrToken,
    BinaryXorToken,
    class_name="BinaryToken"
)

AdditiveToken = Token.any(
    PlusToken,
    MinusToken,
    class_name="AdditiveToken"
)

MultiplicativeToken = Token.any(
    StarToken,
    DivideToken,
    IntegerDivideToken,
    ModuloToken,
    class_name="MultiplicativeToken"
)

UnaryToken = Token.any(
    NegationToken,
    MinusToken,
    StarToken,
    BinaryNotToken,
    AmpersandToken,
    class_name="UnaryToken"
)

LiteralToken = Token.any(
    NumberToken,
    CharLiteralToken,
    StringLiteralToken,
    BoolLiteralToken,
    class_name="LiteralToken"
)


