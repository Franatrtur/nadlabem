import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.compiler import Compiler
from src.config import CompilationConfig

PROGRAM = """
def load_file(arg_by_ref: @int) -> void {
    arg_by_ref = 8
}

length: bool = true

x: int = int(length) * 5

load_file(*x)


z: double = double(5)
y: double = double(10)
z = double^(x) + y
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