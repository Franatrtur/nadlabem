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
        if string.startswith("'"):
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
        
        else:
            try:
                self.value = int(string[:-1])
            except Exception as e:
                raise SymbolError("Invalid char literal", line)
            if not 0 <= self.value <= 255:
                raise SymbolError("Invalid ASCII character in char literal", line)

    @staticmethod
    def detect(string: str) -> bool:
        return string.startswith("'") or (string.endswith("c") and string[:-1].isnumeric())


class StringLiteralToken(Token):
    def __init__(self, string: str, line: Line):
        super().__init__(string, line)
        try:
            self.value = ast.literal_eval(string)
        except Exception as e:
            raise SymbolError("Invalid string literal", line)
        self.bytes: bytes = bytes(self.value, encoding='utf8') + b'\0'
    
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


IncludeToken = Token.literal("include", "IncludeToken")

IfToken = Token.literal("if", "IfToken")
ElseToken = Token.literal("else", "ElseToken")
DoToken = Token.literal("do", "DoToken")
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
DoubleToken = Token.literal("double", "DoubleToken")


class NameToken(Token):
    @staticmethod
    def detect(string: str) -> bool:
        return string[0].isalpha() or string[0] == "_"


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

SignedLessThanToken = Token.literal("<+", "SignedLessThanToken")
SignedGreaterThanToken = Token.literal(">+", "SignedGreaterThanToken")
SignedIsLtEqToken = Token.literal("<~", "SignedIsLtEqToken")
SignedIsGtEqToken = Token.literal("~>", "SignedIsGtEqToken")

EqualsToken = Token.literal("=", "EqualsToken")
AtEqualsToken = Token.literal("=@=", "AtEqualsToken")
IncrementToken = Token.literal("++", "IncrementToken")
DecrementToken = Token.literal("--", "DecrementToken")

CommaToken = Token.literal(",", "CommaToken")
ColonToken = Token.literal(":", "ColonToken")
HashToken = Token.literal("#", "HashToken")
AtToken = Token.literal("@", "AtToken")
ArrowToken = Token.literal("->", "ArrowToken")
DollarToken = Token.literal("$", "DollarToken")

BinaryAndToken = Token.literal("&", "BinaryAndToken")
BinaryOrToken = Token.literal("|", "BinaryOrToken")
BinaryXorToken = Token.literal("^", "BinaryXorToken")
BinaryNotToken = Token.literal("~", "BinaryNotToken")
BinaryShiftRightToken = Token.literal(">>", "BinaryShiftRightToken")
BinaryShiftLeftToken = Token.literal("<<", "BinaryShiftLeftToken")
BinaryRotateRightToken = Token.literal(">>>", "BinaryRotateRightToken")
BinaryShiftLeftToken = Token.literal("<<<", "BinaryShiftLeftToken")

PlusToken = Token.literal("+", "PlusToken")
MinusToken = Token.literal("-", "MinusToken")
StarToken = Token.literal("*", "StarToken")
DivideToken = Token.literal("/", "DivideToken")
SignedDivideToken = Token.literal("//", "SignedDivideToken")
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
    #dummy method
    @staticmethod
    def detect(string: str) -> bool:
        return string == "\n"


#order matters as priority is used for detection
TOKEN_DETECTORS = [
    NumberToken,
    CharLiteralToken,
    StringLiteralToken,
    CommentToken,

    BoolLiteralToken,

    IncludeToken,

    IfToken,
    ElseToken,
    DoToken,
    WhileToken,
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
    DoubleToken,

    NameToken,

    IsEqualToken,
    IsNotEqualToken,
    IsGtEqToken,
    IsLtEqToken,
    GreaterThanToken,
    LessThanToken,
    SignedLessThanToken,
    SignedGreaterThanToken,
    SignedIsLtEqToken,
    SignedIsGtEqToken,

    EqualsToken,
    AtEqualsToken,
    IncrementToken,
    DecrementToken,

    LogicalAndToken,
    LogicalOrToken,
    LogicalNotToken,

    CommaToken,
    ColonToken,
    HashToken,
    AtToken,
    ArrowToken,
    DollarToken,

    BinaryAndToken,
    BinaryOrToken,
    BinaryXorToken,
    BinaryNotToken,

    BinaryShiftRightToken,
    BinaryShiftLeftToken,
    BinaryRotateRightToken,
    BinaryShiftLeftToken,

    PlusToken,
    MinusToken,
    StarToken,
    DivideToken,
    SignedDivideToken,
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
    DoubleToken,
    class_name="TypeToken"
)

KeywordToken = Token.any(
    IfToken,
    DoToken,
    WhileToken,
    ElseToken,
    ForToken,
    ReturnToken,
    BreakToken,
    ContinueToken,
    PassToken,
    DefinitionToken,
    IncludeToken,
    class_name="KeywordToken"
)

IncrementalToken = Token.any(
    IncrementToken,
    DecrementToken,
    class_name="IncrementalToken"
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
    SignedLessThanToken,
    SignedGreaterThanToken,
    SignedIsLtEqToken,
    SignedIsGtEqToken,
    class_name="ComparisonToken"
)

BinaryToken = Token.any(
    BinaryAndToken,
    BinaryOrToken,
    BinaryXorToken,
    BinaryShiftRightToken,
    BinaryShiftLeftToken,
    BinaryRotateRightToken,
    BinaryShiftLeftToken,
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
    SignedDivideToken,
    ModuloToken,
    class_name="MultiplicativeToken"
)

UnaryToken = Token.any(
    LogicalNotToken,
    MinusToken,
    BinaryNotToken,
    class_name="UnaryToken"
)

LiteralToken = Token.any(
    NumberToken,
    CharLiteralToken,
    StringLiteralToken,
    BoolLiteralToken,
    class_name="LiteralToken"
)


