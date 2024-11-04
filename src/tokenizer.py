import re, ast
from typing import Type
from .errors import SyntaxError, ParsingError, NadLabemError


class Token:

    def __init__(self, string: str):
        self.string = string

    def __str__(self):
        return f"{self.__class__.__name__}(\"{self.string}\")"

    @staticmethod
    def literal(string: str, class_name: str) -> Type['Token']:
        # Define a new subclass of Token with a custom detect method, case insensitive
        return type(class_name, (Token,), {
            "detect": staticmethod(lambda s: s.lower() == string.lower()),
        })

    @classmethod
    def match(cls, token: 'Token') -> bool:
        # Checks if the token is exactly an instance of the calling class
        return isinstance(token, cls)

    @staticmethod
    def any(*classes: Type["Token"], class_name: str = "CombinedToken") -> Type["Token"]:
        # Define a new subclass of Token with a custom detect method
        return type(class_name, (Token,), {
            "detect": staticmethod(lambda s: any(cls.detect(s) for cls in classes)),
            "match": classmethod(lambda cls, token: any(cls.match(token) for cls in classes))
        })



class NumberLiteralToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
        if string.lower().endswith("h"):
            self.value = int(string[0:-1], 16)
        else:
            try:
                self.value = ast.literal_eval(string)
            except SyntaxError as e:
                raise Exception("Invalid number literal")
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.isnumeric() or re.match(r"^[0-9a-fA-F]+h$", string) or re.match(r"^0x[0-9a-fA-F]+$", string)

class StringLiteralToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
        try:
            self.value = ast.literal_eval(string)
        except Exception as e:
            raise Exception("Invalid string literal")
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.startswith("\"") or string.startswith("'")

class CommentToken(Token):
    @staticmethod
    def detect(string: str) -> bool:
        return string.startswith(";")


IfToken = Token.literal("if", "IfToken")
ThenToken = Token.literal("then", "ThenToken")
WhileToken = Token.literal("while", "WhileToken")
ElseToken = Token.literal("else", "ElseToken")
ForToken = Token.literal("for", "ForToken")

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

PlusToken = Token.literal("+", "PlusToken")
MinusToken = Token.literal("-", "MinusToken")
MultiplyToken = Token.literal("*", "MultiplyToken")
DivideToken = Token.literal("/", "DivideToken")

OpenParenToken = Token.literal("(", "OpenParenToken")
CloseParenToken = Token.literal(")", "CloseParenToken")


CodeBlockBeginToken = Token.literal("{", "CodeBlockBeginToken")
CodeBlockEndToken = Token.literal("}", "CodeBlockEndToken")

class IgnoreToken(Token):
    @staticmethod
    def detect(string: str) -> bool:
        return True


#order matters as priority is used for detection
TOKEN_DETECTORS = [
    NumberLiteralToken,
    StringLiteralToken,
    CommentToken,

    IfToken,
    ThenToken,
    WhileToken,
    ElseToken,
    ForToken,

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

    PlusToken,
    MinusToken,
    MultiplyToken,
    DivideToken,

    OpenParenToken,
    CloseParenToken,

    CodeBlockBeginToken,
    CodeBlockEndToken,
]


#Good-to-have token types
KeywordToken = Token.any(IfToken, ElseToken, ThenToken, WhileToken, ForToken, class_name="KeywordToken")
AlgebraicToken = Token.any(PlusToken, MinusToken, MultiplyToken, DivideToken, class_name="AlgebricToken")
ComparisonToken = Token.any(IsEqualToken, IsGtEqToken, IsLtEqToken, LessThanToken, GreaterThanToken, class_name="ComparisonToken")
LiteralToken = Token.any(NumberLiteralToken, StringLiteralToken, class_name="LiteralToken")
ValueToken = Token.any(NameToken, LiteralToken, class_name="ValueToken")


class Line:
    def __init__(self, string: str, number: int):
        self.string = string
        self.number = number
        self.tokens: list[Token] = []
        self.comment: str = ""

    def pushToken(self, token: Token) -> None:
        token.line = self
        if CommentToken.match(token):
            self.comment = token.string
        else:
            self.tokens.append(token)

    def __str__(self):
        return f"Line {self.number}: \"{self.string}\" [{','.join(map(str, self.tokens))}\"]"
    def __repr__(self):
        return str(self)



def split_tokens(line_string: str) -> list[str]:
    # Regular expression to match words, numbers, and punctuation, newly also strings and comments
    pattern = r""";.*|>=|==|!=|<=|"(?:\\"|[^"])*"|'(?:\\'|[^'])*'|\b\w+\b|[^\w\s]"""
    tokens = re.findall(pattern, line_string)

    return tokens


def tokenize(line_string: str, line_number: int | None = None) -> Line:
    token_strings = split_tokens(line_string)
    line = Line(line_string, line_number)

    for token_string in token_strings:

        try:
            token: Token = None

            for token_type in TOKEN_DETECTORS:

                if token_type.detect(token_string):
                    token = token_type(token_string)
                    line.pushToken(token)
                    break

            if not token:
                raise SyntaxError(f"Unexpected \"{token_string}\"", f"Line {line_number}: \"{line_string}\"")

        except Exception as e:
            if isinstance(e, NadLabemError):
                raise e
            else:
                raise SyntaxError(f"{str(e)}. Unexpected \"{token_string}\"", f"Line {line_number}: \"{line_string}\"")


    return line


def match_token_pattern(line: Line | list[Token], token_types: list[Type[Token]], ignore_subsequent_tokens: bool = False) -> bool:

    if isinstance(line, Line):
        line = line.tokens

    # First check if we have enough tokens to match the pattern
    # Check if pattern matches for the required token types
    length_match = len(line) >= len(token_types) if ignore_subsequent_tokens else len(line) == len(token_types)

    return length_match and all(
        token_types[i].match(line[i])
        for i in range(len(token_types))
    )
