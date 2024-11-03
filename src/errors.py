

class NadLabemError(Exception):

    def __init__(self, error_string: str, line: "Line", **kwargs):
        self.error_string = error_string
        self.line = line
        self.kwargs = kwargs

    def __str__(self):
        return f"{self.error_string} on {self.line}, {self.kwargs}"


class NameError(NadLabemError):
    pass

class SyntaxError(NadLabemError):
    pass

class ParsingError(NadLabemError):
    pass