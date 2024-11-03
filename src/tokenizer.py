import re
from typing import Type


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



class NumberToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
        self.value = int(string) if string.isnumeric() else int(string[0:-1], 16)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.isnumeric() or re.match(r"^[0-9a-fA-F]+h$", string) #hex numbers

DefineByteToken = Token.literal("db", "DefineByteToken")
HaltToken = Token.literal("hlt", "HaltToken")

IfToken = Token.literal("if", "IfToken")
ThenToken = Token.literal("then", "ThenToken")
WhileToken = Token.literal("while", "WhileToken")
ElseToken = Token.literal("else", "ElseToken")
ForToken = Token.literal("for", "ForToken")
EndToken = Token.literal("end", "EndToken")

class NameToken(Token):
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.isalpha()

EqualsToken = Token.literal("=", "EqualsToken")
NegationToken = Token.literal("!", "NegationToken")

SemicolonToken = Token.literal(";", "SemicolonToken")
CommaToken = Token.literal(",", "CommaToken")

PlusToken = Token.literal("+", "PlusToken")
MinusToken = Token.literal("-", "MinusToken")
MultiplyToken = Token.literal("*", "MultiplyToken")
DivideToken = Token.literal("/", "DivideToken")

OpenParenToken = Token.literal("(", "OpenParenToken")
CloseParenToken = Token.literal(")", "CloseParenToken")

LessThanToken = Token.literal("<", "RelationalToken")
GreaterThanToken = Token.literal(">", "RelationalToken")

CodeBlockBeginToken = Token.literal("{", "CodeBlockBeginToken")
CodeBlockEndToken = Token.literal("}", "CodeBlockEndToken")

class IgnoreToken(Token):
    
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

    NameToken,

    EqualsToken,
    NegationToken,

    SemicolonToken,
    CommaToken,

    PlusToken,
    MinusToken,
    MultiplyToken,
    DivideToken,

    OpenParenToken,
    CloseParenToken,

    LessThanToken,
    GreaterThanToken,

    CodeBlockBeginToken,
    CodeBlockEndToken,
]


#Good-to-have token types
KeywordToken = Token.any(IfToken, ElseToken, EndToken, ThenToken, WhileToken, ForToken, class_name="KeywordToken")

AlgebraicToken = Token.any(PlusToken, MinusToken, MultiplyToken, DivideToken, class_name="AlgebricToken")

RelationalToken = Token.any(LessThanToken, GreaterThanToken, class_name="RelationalToken")


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
    
    comment_state = False  # is set to True once ; is encountered

    for token_string in token_strings:

        token: Token = None

        if comment_state:
            token = IgnoreToken(token_string)
            line.pushToken(token)
            continue

        for token_type in TOKEN_TYPES:

            if token_type.detect(token_string):

                if token_type is SemicolonToken:
                    comment_state = True
                    token_type = IgnoreToken

                token = token_type(token_string)
                break

        if not token:
            raise f"Unexpected \"{str}\" - Unknown token"

        line.pushToken(token)

    return line


def match_token_pattern(line: Line, token_types: list[Type[Token]], ignore_subsequent_tokens: bool = False, ignore_commented_tokens: bool = True) -> bool:
    
    # First check if we have enough tokens to match the pattern
    if len(line.tokens) < len(token_types):
        return False

    # Check if pattern matches for the required token types
    pattern_match = all(
        token_types[i].match(line.tokens[i])
        for i in range(len(token_types))
    )

    if not pattern_match:
        return False

    # If we don't need to check subsequent tokens, we're done
    if not ignore_subsequent_tokens:
        # Check remaining tokens after pattern match
        # Only return True if all remaining tokens are ignored tokens (when ignore_commented_tokens is True)
        remaining_tokens = line.tokens[len(token_types):]
        if remaining_tokens:
            return all(
                IgnoreToken.match(token) and ignore_commented_tokens
                for token in remaining_tokens
            )
        return True

    # If we need exact match, verify no extra tokens
    return len(line.tokens) == len(token_types)
