class LexicalError(Exception):
    """Exception raised for errors during the tokenizing phase."""
    pass

class SyntaxError(Exception):
    """Exception raised for errors during the parsing phase."""
    pass

class TranslationError(Exception):
    """Exception raised for errors during the translating phase."""
    pass