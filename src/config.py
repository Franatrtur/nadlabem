from.errors import NadLabemError

class CompilationConfig:

    def __init__(self,
            target_cpu: str = "i8086",
            strict: bool = True,
            generate_mapping: bool = True,
            erase_comments: bool = False,
            tabspaces: int = 8,
            verbose: bool = True):

        self.target_cpu = target_cpu
        self.strict = strict
        self.generate_mapping = generate_mapping
        self.erase_comments = erase_comments
        self.tabspaces = tabspaces
        self.verbose = verbose

        self.compiler: "Compiler" = None

    def warn(self, error: NadLabemError) -> None:
        if self.strict:
            error.kwargs["strict"] = "Error raised because strict mode is on"
            raise error
        error.warning = True
        self.compiler.warnings.append(error)

    def __str__(self):
        return f"CompilationConfig(target_cpu={self.target_cpu}, strict={self.strict}, generate_mapping={self.generate_mapping}, erase_comments={self.erase_comments}, tabspaces={self.tabspaces}, verbose={self.verbose})"