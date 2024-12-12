

class NadLabemError(Exception):

    def __init__(self, error_string: str, line: "Line", **kwargs):
        self.error_string = error_string
        self.line = line
        self.kwargs = kwargs
        self.warning: bool = False

    def __str__(self):
        print()
        if self.warning:
            label = self.__class__.__name__[:-5] + " Warning:"
            color = "\033[33m"
        else:
            label = self.__class__.__name__
            color = "\033[41m "
        additional = f"\n\nAdditional info: {self.kwargs}" if self.kwargs else ""
        return f"\n\n{color}{label} \033[0m {self.error_string} on {self.line}" + additional


class NameError(NadLabemError):
    pass

class SyntaxError(NadLabemError):
    pass

class SymbolError(NadLabemError):
    pass

class TypeError(NadLabemError):
    pass

class NotImplementedError(NadLabemError):
    pass