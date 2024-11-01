import re
from typing import Type

#TODO: add if while and other tokens


class Token:
    def __init__(self, string: str):
        self.string = string

    def __str__(self):
        return f"{self.__class__.__name__}(\"{self.string}\")"

    @staticmethod
    def literal(string: str, class_name: str) -> Type['Token']:
        # Define a new subclass of Token with a custom detect method
        return type(class_name, (Token,), {
            "detect": staticmethod(lambda s: s.lower() == string.lower()),
        })

    @classmethod
    def match(cls, token: 'Token') -> bool:
        # Checks if the token is exactly an instance of the calling class
        return isinstance(token, cls)



class NumberToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
        self.value = int(string) if string.isnumeric() else int(string[0:-1], 16)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.isnumeric() or re.match(r"^[0-9a-fA-F]+h$", string) #hex numbers


DefineByteToken = Token.literal("db", "DefineByteToken")

IfToken = Token.literal("if", "IfToken")

ThenToken = Token.literal("then", "ThenToken")

WhileToken = Token.literal("while", "WhileToken")

ElseToken = Token.literal("else", "ElseToken")

ForToken = Token.literal("for", "ForToken")

EndToken = Token.literal("end", "EndToken")


#falling through
class KeywordToken(Token):

    def __init__(self, string):
        raise f"Missing token for {string}, fell through to KeywordToken"
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.lower() in ["if", "then", "while", "else", "for", "end"]

class NameToken(Token):
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.isalpha()


EqualsToken = Token.literal("=", "EqualsToken")

SemicolonToken = Token.literal(";", "SemicolonToken")

PlusToken = Token.literal("+", "PlusToken")

MinusToken = Token.literal("-", "MinusToken")

MultiplyToken = Token.literal("*", "MultiplyToken")

DivideToken = Token.literal("/", "DivideToken")

RelationalToken = Token.literal("<>", "RelationalToken")

CodeBlockBeginToken = Token.literal("{", "CodeBlockBeginToken")

CodeBlockEndToken = Token.literal("}", "CodeBlockEndToken")

class UnknownToken(Token):
    
    @staticmethod
    def detect(string: str) -> bool:
        return True


#order matters as priority is used for detection
TOKEN_TYPES = [
    NumberToken,

    DefineByteToken,

    IfToken,
    ThenToken,
    WhileToken,
    ElseToken,
    ForToken,
    EndToken,

    KeywordToken, #not used

    NameToken,

    EqualsToken,
    SemicolonToken,
    PlusToken,
    MinusToken,
    MultiplyToken,
    DivideToken,
    RelationalToken,

    CodeBlockBeginToken,
    CodeBlockEndToken,

    UnknownToken
]


class Line:
    def __init__(self, string: str, number: int):
        self.string = string
        self.number = number
        self.tokens: list[Token] = []

    def pushToken(self, token: Token):
        self.tokens.append(token)
        token.line = self
        token.line_number = self.number
        token.line_string = self.string

    def __str__(self):
        return f"Line {self.number}: \"{self.string}\" [{','.join(map(str, self.tokens))}\"]"



def split_tokens(line_string: str) -> list[str]:
    # Regular expression to match words, numbers, and punctuation
    pattern = r"\b\w+\b|[^\w\s]"
    tokens = re.findall(pattern, line_string)

    return tokens


def tokenize(line_string: str, line_number: int | None = None) -> Line:
    token_strings = split_tokens(line_string)
    line = Line(line_string, line_number)

    for token_string in token_strings:
        for token_type in TOKEN_TYPES:
            if token_type.detect(token_string):

                line.pushToken(token_type(token_string))
                break

    return line


def match_token_pattern(line: Line, token_types: list[Type[Token]], ignore_subsequent_tokens: bool = False) -> bool:
    length_match = False

    if ignore_subsequent_tokens:
        length_match = len(line.tokens) >= len(token_types)
    else:
        length_match = len(line.tokens) == len(token_types)

    if not length_match:
        return False

    return all(token_types[i].match(line.tokens[i]) for i in range(len(token_types)))



