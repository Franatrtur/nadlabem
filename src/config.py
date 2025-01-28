from.errors import NadLabemError
from pathlib import Path


class CompilationConfig:

    def __init__(self,
            target: str = "i8086",
            location: Path | None = None,
            strict: bool = True,
            generate_mapping: bool = True,
            erase_comments: bool = False,
            tabspaces: int = 8,
            verbose: bool = True,
            obfuscate: bool = False,
            optimize: bool = True):

        self.location: Path | None = location
        self.target: str = target
        self.strict: bool = strict
        self.generate_mapping: bool = generate_mapping
        self.erase_comments: bool = erase_comments
        self.tabspaces: int = tabspaces
        self.verbose: bool = verbose
        self.obfuscate: bool = obfuscate
        self.optimize: bool = optimize

        self.compiler: "Compiler" = None

    def warn(self, error: NadLabemError) -> None:
        if self.strict:
            error.kwargs["strict"] = "Error raised because strict mode is on"
            raise error
        error.warning = True
        self.compiler.warnings.append(error)

    def __str__(self):
        return f"CompilationConfig(target={self.target}, strict={self.strict}, generate_mapping={self.generate_mapping}, erase_comments={self.erase_comments}, tabspaces={self.tabspaces}, ...)"