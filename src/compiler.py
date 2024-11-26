from .errors import NadLabemError
from .config import CompilationConfig
from .tokenizer import Tokenizer
from .parser.program import ProgramParser
from .targets import TARGETS, Translator
from typing import Type

class Compiler:

    def __init__(self, config: CompilationConfig):
        self.config = config
        self.config.compiler = self
        self.warnings: list[NadLabemError] = []

        if self.config.target_cpu not in TARGETS:
            raise NadLabemError(f"Invalid target CPU: {self.config.target_cpu}", line="in the compilation config")

        self.target: list[Type[Translator]] = TARGETS[self.config.target_cpu]

    def compile(self, source_code: str):
        self.load(source_code)
        self.tokenize()
        self.parse()
        self.translate()

    def load(self, source_code: str):
        self.source_code = source_code

    def tokenize(self):
        self.tokens = Tokenizer(compiler=self).tokenize(self.source_code)

    def parse(self):
        self.tree = ProgramParser(self.tokens, compiler=self).parse()
        self.tree.validate()

    def translate(self):
        self.machine_code = self.tree.translate()