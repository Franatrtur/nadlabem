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
ReturnToken = Token.literal("return", "ReturnToken")
BreakToken = Token.literal("break", "BreakToken")
ContinueToken = Token.literal("continue", "ContinueToken")
PassToken = Token.literal("pass", "PassToken")

LogicalAndToken = Token.literal("and", "LogicalAndToken")
LogicalOrToken = Token.literal("or", "LogicalOrToken")
LogicalNotToken = Token.literal("not", "LogicalNotToken")

IntToken = Token.literal("int", "IntToken")
UIntToken = Token.literal("uint", "UIntToken")
StringToken = Token.literal("string", "StringToken")
BoolToken = Token.literal("bool", "BoolToken")
ArrayToken = Token.literal("array", "ArrayToken")
CharToken = Token.literal("char", "CharToken")
VoidToken = Token.literal("void", "VoidToken")


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

BinaryAndToken = Token.literal("&", "BinaryAndToken")
BinaryOrToken = Token.literal("|", "BinaryOrToken")
BinaryXorToken = Token.literal("^", "BinaryXorToken")
BinaryNotToken = Token.literal("~", "BinaryNotToken")

PlusToken = Token.literal("+", "PlusToken")
MinusToken = Token.literal("-", "MinusToken")
MultiplyToken = Token.literal("*", "MultiplyToken")
DivideToken = Token.literal("/", "DivideToken")
IntegerDivideToken = Token.literal("//", "IntegerDividToken")
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
    IntegerLiteralToken,
    StringLiteralToken,
    CommentToken,

    IfToken,
    WhileToken,
    ElseToken,
    ForToken,
    ReturnToken,
    BreakToken,
    ContinueToken,
    PassToken,

    LogicalAndToken,
    LogicalOrToken,
    LogicalNotToken,

    IntToken,
    UIntToken,
    StringToken,
    BoolToken,
    ArrayToken,
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

    BinaryAndToken,
    BinaryOrToken,
    BinaryXorToken,
    BinaryNotToken,

    PlusToken,
    MinusToken,
    MultiplyToken,
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


KeywordToken = Token.any(
    IfToken,
    WhileToken,
    ElseToken,
    ForToken,
    ReturnToken,
    BreakToken,
    ContinueToken,
    PassToken,
    VoidToken,
    class_name="KeywordToken"
)

StatementBeginToken = Token.any(
    KeywordToken,
    HashToken,
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
    BinaryAndToken,
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
    MultiplyToken,
    DivideToken,
    IntegerDivideToken,
    ModuloToken,
    class_name="MultiplicativeToken"
)

UnaryToken = Token.any(
    NegationToken,
    MinusToken,
    MultiplyToken,
    BinaryNotToken,
    class_name="UnaryToken"
)

TypeToken = Token.any(
    IntToken,
    UIntToken,
    StringToken,
    BoolToken,
    ArrayToken,
    CharToken,
    VoidToken,
    class_name="TypeToken"
)

LiteralToken = Token.any(
    IntegerLiteralToken,
    StringLiteralToken,
    class_name="LiteralToken"
)


