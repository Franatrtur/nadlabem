import re

Token = str

def tokenize(line: str) -> list[Token]:
    # Regular expression to match words, numbers, and punctuation
    pattern = r"\b\w+\b|[^\w\s]"
    tokens = re.findall(pattern, line)

    return tokens
