import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.compiler import Compiler
from src.config import CompilationConfig

PROGRAM = """
bool a = False
char b = 0 + a
#navesti hlt
"""

if __name__ == "__main__":
    compiler = Compiler(CompilationConfig())
    #print(f"{compiler=}")
    compiler.load(PROGRAM)
    #print(f"{compiler.source_code=}")
    compiler.tokenize()
    #print(f"{compiler.tokens=}")
    compiler.parse()
    print(compiler.tree)
    compiler.translate()
    print('\n'.join(compiler.machine_code))