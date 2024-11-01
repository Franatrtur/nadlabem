import re

#TODO: add if while and other tokens

class Token:
    def __init__(self, string: str):
        self.string = string

    def __str__(self):
        return f"{self.__class__.__name__}(\"{self.string}\")"


class NumberToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
        self.value = int(string) if string.isnumeric() else int(string[0:-1], 16)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.isnumeric() or re.match(r"^[0-9a-fA-F]+h$", string) #hex numbers

class KeywordToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.lower() in ["if", "then", "while", "else", "for", "end"]

class NameToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string.isalpha()

class EqualsToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string == "="

class SemicolonToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string == ";"

class PlusToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string in "+"

class MinusToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string in "-"

class MultiplyToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string in "*"

class DivideToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string in "/"

class RelationalToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string in "<>"

class CodeBlockBeginToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string == "{"

class CodeBlockEndToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
    
    @staticmethod
    def detect(string: str) -> bool:
        return string == "}"

class UnknownToken(Token):
    def __init__(self, string: str):
        super().__init__(string)
    
    @staticmethod
    def detect(string: str) -> bool:
        return True


#order matters as priority is used for detection
TOKEN_TYPES = [
    NumberToken,
    KeywordToken,
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
        return f"Line[{','.join(map(str, self.tokens))}\"]"



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



