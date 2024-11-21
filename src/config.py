from.errors import NadLabemError

class CompilationConfig:

    def __init__(self,
            target_cpu: str = "i8086",
            strict: bool = True,
            generate_mapping: bool = True,
            devmode: bool = False,
            erase_comments: bool = False,
            tabspaces: int = 8,
            verbose: bool = True):

        self.target_cpu = target_cpu
        self.strict = strict
        self.generate_mapping = generate_mapping
        self.devmode = devmode
        self.erase_comments = erase_comments
        self.tabspaces = tabspaces
        self.verbose = verbose

        self.compiler: "Compiler" = None

    def warn(self, error: NadLabemError) -> None:
        if self.strict:
            raise error
        error.warning = True
        self.compiler.warnings.append(error)

    def __str__(self):
        return f"TranslationConfig(target_cpu={self.target_cpu}, strict={self.strict}, generate_mapping={self.generate_mapping}, devmode={self.devmode}, erase_comments={self.erase_comments}, tabspaces={self.tabspaces}, verbose={self.verbose})"