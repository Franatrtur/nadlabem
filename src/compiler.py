from .errors import NadLabemError
from .config import CompilationConfig
from .tokenizer import Tokenizer
from .parser.program import ProgramParser
from typing import Type
from .tree import Node
from pathlib import Path
from .targets import CompilationTarget

class Compiler:

    def __init__(self, config: CompilationConfig):
        self.config = config
        self.config.compiler = self
        self.warnings: list[NadLabemError] = []

        if self.config.target not in CompilationTarget.targets:
            raise NadLabemError(f"Invalid compilation target: {self.config.target_cpu}", line="in the compilation config")

        self.target: CompilationTarget = CompilationTarget.targets[self.config.target]

    def compile(self, source_code: str) -> str:
        self.load(source_code)
        self.tokenize()
        self.parse()
        self.translate()
        return self.export()

    def load(self, source_code: str | Path) -> None:
        if isinstance(source_code, Path):
            self.location = source_code
            source_code = source_code.read_text()
        self.source_code = source_code
        return self

    def tokenize(self) -> None:
        self.tokens = Tokenizer(config=self.config, location=self.config.location).tokenize(self.source_code)

    def parse(self) -> None:
        self.tree = ProgramParser(self.tokens, config=self.config).parse()
        self.tree.validate()

    def translate(self) -> None:
        self.machine_code: list[str] = [str(asmline) for asmline in self.target.entry_point(self).translate()]
        if self.config.generate_mapping:
            self.machine_code = DISCLAIMER + self.machine_code

    def export(self) -> str:
        return "\n".join(self.machine_code)


DISCLAIMER = ["; << Generated by NadLabem >>", "; the open source brandejs-to-assembly compiler", ""]