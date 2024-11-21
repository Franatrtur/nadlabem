import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.compiler import Compiler
from src.config import CompilationConfig

PROGRAM = """
int pointer_to_x = *x   ;#0x3e4f
; same thing:
int* y = *x  ; y now references the same part of memory as x, as we defined it not by value, but by pointer

def void print_number(int _) pass

print_number(y) ; print 2
int* x = 2  ; we load 2 as the pointer, but should throw errow when strict 

y = y + 1     ; x is also now 3
print_number(x) ; prints 3
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
    # compiler.translate()
    # print(f"{compiler.machine_code=}")