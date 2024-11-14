import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.compiler import Compiler
from src.config import CompilationConfig

PROGRAM = """
string mystring = "ahoj jak se mas"

y=fn(x-y)"""

if __name__ == "__main__":
    compiler = Compiler(CompilationConfig())
    print(f"{compiler=}")
    compiler.load(PROGRAM)
    print(f"{compiler.source_code=}")
    compiler.tokenize()
    print(f"{compiler.tokens=}")
    compiler.parse()
    print(compiler.tree)
    # compiler.translate()
    # print(f"{compiler.machine_code=}")