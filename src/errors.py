

class NadLabemError(Exception):

    def __init__(self, error_string: str, line: "Line", **kwargs):
        self.error_string = error_string
        self.line = line
        self.kwargs = kwargs
        print()

    def __str__(self):
        return f"\n\n\33[41m {self.__class__.__name__} \033[0m {self.error_string} on {self.line}, {self.kwargs}"


class NameError(NadLabemError):
    pass

class SyntaxError(NadLabemError):
    pass

class SymbolError(NadLabemError):
    pass