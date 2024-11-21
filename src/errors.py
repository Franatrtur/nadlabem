

class NadLabemError(Exception):

    def __init__(self, error_string: str, line: "Line", **kwargs):
        self.error_string = error_string
        self.line = line
        self.kwargs = kwargs
        self.warning: bool = False
        print()

    def __str__(self):
        if self.warning:
            label = self.__class__.__name__[:-5] + " Warning:"
            color = "\033[33m"
        else:
            label = self.__class__.__name__
            color = "\033[41m "
        return f"\n\n{color}{label} \033[0m {self.error_string} on {self.line}\nAdditional info: {self.kwargs}"


class NameError(NadLabemError):
    pass

class SyntaxError(NadLabemError):
    pass

class SymbolError(NadLabemError):
    pass

class TypeError(NadLabemError):
    pass
