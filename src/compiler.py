from .errors import NadLabemError
from .config import CompilationConfig
from .tokenizer import Tokenizer
from .parser.program import ProgramParser
from .targets import TARGETS, Translator, ProgramTranslator, ENTRY_POINTS
from typing import Type

class Compiler:

    def __init__(self, config: CompilationConfig):
        self.config = config
        self.config.compiler = self
        self.warnings: list[NadLabemError] = []

        if self.config.target_cpu not in TARGETS:
            raise NadLabemError(f"Invalid target CPU: {self.config.target_cpu}", line="in the compilation config")

        self.target: list[Type[Translator]] = TARGETS[self.config.target_cpu]
        self.entry_translator: Type[ProgramTranslator] = ENTRY_POINTS[self.config.target_cpu]

    def compile(self, source_code: str) -> str:
        self.load(source_code)
        self.tokenize()
        self.parse()
        self.translate()
        return "\n".join(self.machine_code)

    def load(self, source_code: str) -> None:
        self.source_code = source_code

    def tokenize(self) -> None:
        self.tokens = Tokenizer(compiler=self).tokenize(self.source_code)

    def parse(self) -> None:
        self.tree = ProgramParser(self.tokens, compiler=self).parse()
        self.tree.validate()

    def translate(self) -> None:
        self.machine_code: list[str] = self.entry_translator(self).translate()