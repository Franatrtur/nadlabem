from .errors import NadLabemError
from .config import CompilationConfig
from .tokenizer import tokenize_source_code, Line, Token
from .parser.program import ProgramParser

class Compiler:

    def __init__(self, config: CompilationConfig):
        self.config = config

    def compile(self, source_code: str):
        self.load(source_code)
        self.tokenize()
        self.parse()
        self.translate()

    def load(self, source_code: str):
        self.source_code = source_code

    def tokenize(self):
        self.tokens = tokenize_source_code(self.source_code)

    def parse(self):
        self.tree = ProgramParser(self.tokens, compiler=self).parse()

    def translate(self):
        self.machine_code = self.tree.translate()